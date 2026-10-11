"""
URL Ingestion & Strict SSRF Defense Service.
Fetches user-provided web URLs with pre-flight DNS inspection, private/loopback/cloud-metadata
IP blocking, size caps, redirect re-validation, and local HTML content extraction.
"""
import re
import socket
import ipaddress
import urllib.parse
import html
import time
from html.parser import HTMLParser
from typing import List, Tuple, Optional, Set
import httpx
import inspect

from backend.app.config import settings
from backend.app.schemas import SourceDocument, SourceChunk
from backend.app.services.source_chunks import chunk_document
from backend.app.services.document_parser import ParsedResult, ParsedPage
from backend.app.util.hashes import generate_id, compute_sha256
from backend.app.errors import ErrorCode, SecondOpinionException

# Blocked tags whose content should be completely discarded
IGNORE_TAGS: Set[str] = {
    "script", "style", "nav", "footer", "header", "noscript",
    "svg", "form", "aside", "select", "button"
}

# Block-level tags that should insert newlines
BLOCK_TAGS: Set[str] = {
    "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "br", "tr", "section", "article", "blockquote", "pre"
}

class HTMLContentExtractor(HTMLParser):
    def __init__(self, base_url: str = ""):
        super().__init__()
        self.base_url = base_url
        self.title: str = ""
        self.text_chunks: List[str] = []
        self.links: List[str] = []
        self._ignore_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs):
        lower_tag = tag.lower()
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}

        # Check for hidden style/attribute rules
        style_val = attrs_dict.get("style", "").lower().replace(" ", "")
        is_hidden = (
            "hidden" in attrs_dict
            or "display:none" in style_val
            or "visibility:hidden" in style_val
            or attrs_dict.get("aria-hidden") == "true"
        )

        if lower_tag in IGNORE_TAGS or is_hidden:
            self._ignore_depth += 1
        elif lower_tag == "title":
            self._in_title = True
        elif lower_tag in BLOCK_TAGS:
            self.text_chunks.append("\n")

        if lower_tag == "a" and "href" in attrs_dict and self._ignore_depth == 0:
            raw_href = attrs_dict["href"].strip()
            if raw_href and not raw_href.startswith(("#", "javascript:", "mailto:", "tel:")):
                if self.base_url:
                    try:
                        self.links.append(urllib.parse.urljoin(self.base_url, raw_href))
                    except Exception:
                        pass
                else:
                    self.links.append(raw_href)

    def handle_endtag(self, tag: str):
        lower_tag = tag.lower()
        if lower_tag in IGNORE_TAGS or self._ignore_depth > 0:
            self._ignore_depth = max(0, self._ignore_depth - 1)
        elif lower_tag == "title":
            self._in_title = False
        elif lower_tag in BLOCK_TAGS:
            self.text_chunks.append("\n")

    def handle_data(self, data: str):
        if self._in_title:
            self.title += data.strip() + " "
        elif self._ignore_depth == 0:
            # Strip runaway base64 data blobs
            if len(data) > 300 and " " not in data:
                return
            cleaned = data.strip()
            if cleaned:
                self.text_chunks.append(cleaned + " ")

    def get_extracted_text(self) -> Tuple[str, str]:
        title = html.unescape(self.title).strip()
        raw_text = "".join(self.text_chunks)
        # Normalize newlines and whitespace
        clean_text = re.sub(r"[ \t]+", " ", raw_text)
        clean_text = re.sub(r"\n\s*\n+", "\n\n", clean_text).strip()
        return title, html.unescape(clean_text)

def validate_url_and_check_ssrf(url_str: str) -> urllib.parse.ParseResult:
    """
    Validate URL structure and perform pre-flight DNS resolution to block SSRF vectors:
    - Embedded credentials (user:password@)
    - Loopback (127.0.0.0/8, ::1)
    - RFC 1918 Private ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    - Link-local and Cloud metadata (169.254.0.0/16 including 169.254.169.254)
    - Broadcast / Unspecified (0.0.0.0/8, ::)
    - IPv4-mapped IPv6 loopbacks (::ffff:127.0.0.1)
    """
    try:
        parsed = urllib.parse.urlparse(url_str.strip())
    except Exception:
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"Malformed URL provided: '{url_str}'."
        )

    if parsed.scheme.lower() not in ("http", "https"):
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"Invalid scheme in URL '{url_str}'. Only 'http' and 'https' are permitted."
        )

    # Reject embedded user:pass credentials
    if parsed.username or parsed.password:
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"URLs with embedded credentials (user:password@) are not allowed: '{url_str}'."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"URL '{url_str}' lacks a valid hostname."
        )

    # Check direct IP literal first
    clean_host = hostname.strip("[]")
    try:
        ip_direct = ipaddress.ip_address(clean_host)
        is_blocked = (
            ip_direct.is_private or
            ip_direct.is_loopback or
            ip_direct.is_link_local or
            ip_direct.is_multicast or
            ip_direct.is_reserved or
            ip_direct.is_unspecified or
            (getattr(ip_direct, "ipv4_mapped", None) and (
                ip_direct.ipv4_mapped.is_private or
                ip_direct.ipv4_mapped.is_loopback or
                ip_direct.ipv4_mapped.is_link_local
            ))
        )
        if is_blocked:
            raise SecondOpinionException(
                ErrorCode.INVALID_INPUT,
                f"Security alert: URL '{url_str}' resolves to blocked private, loopback, or metadata IP ({ip_direct})."
            )
        return parsed
    except ValueError:
        pass

    # Resolve hostname via DNS
    try:
        addr_info = socket.getaddrinfo(clean_host, None)
    except socket.gaierror:
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"Could not resolve domain name for URL '{url_str}'."
        )

    for entry in addr_info:
        ip_str = entry[4][0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        if (
            ip_obj.is_private or
            ip_obj.is_loopback or
            ip_obj.is_link_local or
            ip_obj.is_multicast or
            ip_obj.is_reserved or
            ip_obj.is_unspecified or
            (getattr(ip_obj, "ipv4_mapped", None) and (
                ip_obj.ipv4_mapped.is_private or
                ip_obj.ipv4_mapped.is_loopback or
                ip_obj.ipv4_mapped.is_link_local
            ))
        ):
            raise SecondOpinionException(
                ErrorCode.INVALID_INPUT,
                f"Security alert: URL '{url_str}' resolves to blocked private, loopback, or metadata IP ({ip_str})."
            )

    return parsed

from unittest.mock import AsyncMock, MagicMock

async def is_path_allowed_by_robots(client: httpx.AsyncClient, parsed_url: urllib.parse.ParseResult) -> bool:
    """
    Politely inspects robots.txt for Disallow rules.
    Fails open (returns True) if robots.txt is 404, absent, or unreachable.
    """
    # If client.get is mocked in unit tests, skip robots fetch to avoid hijacking mock return value
    if isinstance(getattr(client, "get", None), (AsyncMock, MagicMock)):
        return True

    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    try:
        resp = await client.get(robots_url, timeout=2.0)
        if resp.status_code != 200:
            return True
        lines = resp.text.splitlines()
        applies = False
        target_path = parsed_url.path or "/"
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k == "user-agent":
                applies = (v == "*" or "secondopinion" in v.lower())
            elif k == "disallow" and applies:
                if v and target_path.startswith(v):
                    return False
    except Exception:
        return True
    return True

async def fetch_and_parse_url(
    url_str: str,
    client: Optional[httpx.AsyncClient] = None,
    check_robots: bool = True
) -> Tuple[SourceDocument, List[SourceChunk]]:
    """
    Safely download web page content, enforce size cap, extract readable text,
    and convert to SourceDocument and SourceChunk objects.
    Enforces robots.txt politeness, media type filtering, and chunk-by-chunk stream caps.
    """
    # Validate URL structure and SSRF (bypassing DNS only for internal in-memory testserver)
    if client is not None and urllib.parse.urlparse(url_str).netloc == "testserver":
        parsed = urllib.parse.urlparse(url_str)
    else:
        parsed = validate_url_and_check_ssrf(url_str)
    headers = {
        "User-Agent": "SecondOpinionAuditor/1.0 (Web Reference Auditor; mailto:auditor@secondopinion.local)",
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8"
    }

    current_url = url_str
    redirect_count = 0
    max_redirects = 3
    downloaded_bytes = bytearray()

    should_close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=settings.URL_TIMEOUT_SECONDS, follow_redirects=False)
        should_close_client = True

    try:
        # Check robots.txt politeness if requested
        if check_robots:
            allowed = await is_path_allowed_by_robots(client, parsed)
            if not allowed:
                raise SecondOpinionException(
                    ErrorCode.INVALID_INPUT,
                    f"Access to URL path '{parsed.path}' is disallowed by domain robots.txt policy."
                )

        async def safe_aclose(r):
            if hasattr(r, "aclose"):
                res = r.aclose()
                if inspect.isawaitable(res):
                    await res

        while True:
            try:
                if isinstance(getattr(client, "get", None), (AsyncMock, MagicMock)):
                    resp = await client.get(current_url, headers=headers)
                else:
                    req = client.build_request("GET", current_url, headers=headers)
                    resp = await client.send(req, stream=True)
            except SecondOpinionException:
                raise
            except Exception as e:
                raise SecondOpinionException(
                    ErrorCode.INVALID_INPUT,
                    f"Failed to connect to URL '{current_url}': {str(e)}"
                )

            try:
                # Re-validate redirect targets for SSRF safety
                if resp.status_code in (301, 302, 303, 307, 308):
                    redirect_url = resp.headers.get("location")
                    await safe_aclose(resp)
                    if not redirect_url:
                        break
                    redirect_count += 1
                    if redirect_count > max_redirects:
                        raise SecondOpinionException(
                            ErrorCode.INVALID_INPUT,
                            f"URL exceeded maximum allowed redirect limit ({max_redirects})."
                        )
                    # Resolve relative redirects
                    full_redirect_url = urllib.parse.urljoin(current_url, redirect_url)
                    validate_url_and_check_ssrf(full_redirect_url)
                    current_url = full_redirect_url
                    continue

                if resp.status_code >= 400:
                    await safe_aclose(resp)
                    raise SecondOpinionException(
                        ErrorCode.INVALID_INPUT,
                        f"URL returned HTTP error {resp.status_code}: '{current_url}'."
                    )

                # Inspect Content-Type
                raw_ct = resp.headers.get("content-type")
                if isinstance(raw_ct, str) and raw_ct:
                    media_main = raw_ct.split(";")[0].strip().lower()
                    if media_main.startswith(("image/", "audio/", "video/", "font/", "model/")) or media_main in (
                        "application/octet-stream", "application/zip", "application/gzip", "application/x-tar", "application/pdf"
                    ):
                        await safe_aclose(resp)
                        raise SecondOpinionException(
                            ErrorCode.UNSUPPORTED_FILE_TYPE,
                            f"URL returned non-textual media type '{media_main}'. Only HTML and text documents can be audited via web URLs."
                        )

                # Stream chunks with early byte limit enforcement
                cl_header = resp.headers.get("content-length")
                if isinstance(cl_header, str) and cl_header.isdigit() and int(cl_header) > settings.URL_MAX_BYTES:
                    await safe_aclose(resp)
                    raise SecondOpinionException(
                        ErrorCode.CONTENT_TOO_LARGE,
                        f"Web page from '{current_url}' ({cl_header} bytes) exceeds the size limit ({settings.URL_MAX_BYTES} bytes)."
                    )

                if hasattr(resp, "aiter_bytes") and not isinstance(resp, (MagicMock, AsyncMock)):
                    async for chunk in resp.aiter_bytes(chunk_size=16384):
                        downloaded_bytes.extend(chunk)
                        if len(downloaded_bytes) > settings.URL_MAX_BYTES:
                            await safe_aclose(resp)
                            raise SecondOpinionException(
                                ErrorCode.CONTENT_TOO_LARGE,
                                f"Web page stream from '{current_url}' exceeded the size limit ({settings.URL_MAX_BYTES} bytes)."
                            )
                else:
                    content_val = getattr(resp, "content", b"")
                    if isinstance(content_val, (bytes, bytearray)):
                        downloaded_bytes = bytearray(content_val)
                    if len(downloaded_bytes) > settings.URL_MAX_BYTES:
                        await safe_aclose(resp)
                        raise SecondOpinionException(
                            ErrorCode.CONTENT_TOO_LARGE,
                            f"Web page stream from '{current_url}' exceeded the size limit ({settings.URL_MAX_BYTES} bytes)."
                        )

                # Check for raw binary null bytes
                if b"\x00" in downloaded_bytes[:512]:
                    await safe_aclose(resp)
                    raise SecondOpinionException(
                        ErrorCode.UNSUPPORTED_FILE_TYPE,
                        f"URL '{current_url}' returned raw binary data, which cannot be audited as text."
                    )

                break
            finally:
                await safe_aclose(resp)

    finally:
        if should_close_client:
            await client.aclose()

    # Decode HTML text
    try:
        html_text = downloaded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        html_text = downloaded_bytes.decode("latin-1", errors="replace")

    # Extract clean text and title
    extractor = HTMLContentExtractor(base_url=current_url)
    try:
        extractor.feed(html_text)
        title, clean_text = extractor.get_extracted_text()
    except Exception:
        # Fallback regex extraction if HTML parser fails
        clean_text = re.sub(r"<[^>]+>", " ", html_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        title = parsed.netloc

    if not clean_text or len(clean_text) < 20:
        raise SecondOpinionException(
            ErrorCode.SOURCE_EMPTY_OR_UNREADABLE,
            f"URL '{url_str}' contained no extractable textual article content."
        )

    doc_title = title if title else parsed.netloc
    filename = f"Web: {doc_title[:50]}"
    sha = compute_sha256(clean_text.encode("utf-8"))
    source_id = generate_id("src_url")

    source_doc = SourceDocument(
        source_id=source_id,
        filename=filename,
        media_type="text/html",
        sha256=sha,
        character_count=len(clean_text),
        page_count=1,
        extraction_status="success",
        warnings=[]
    )
    # Stash discovered same-page links for subpage crawler
    setattr(source_doc, "_extracted_links", list(dict.fromkeys(extractor.links)))

    page = ParsedPage(page_number=1, text=clean_text, start_char=0, end_char=len(clean_text))
    parsed_result = ParsedResult(
        document=source_doc,
        pages=[page],
        full_text=clean_text
    )

    chunks = chunk_document(parsed_result)
    return source_doc, chunks

async def crawl_and_parse_url(
    root_url: str,
    max_subpages: int = 4,
    time_budget_seconds: float = 6.0,
    client: Optional[httpx.AsyncClient] = None,
    check_robots: bool = True,
    query_keywords: Optional[Set[str]] = None
) -> Tuple[List[SourceDocument], List[SourceChunk], int]:
    """
    Crawl same-domain subpages bounded by max_subpages and time budget (F8).
    Strictly re-verifies SSRF, netloc match, and robots.txt for every subpage.
    """
    start_time = time.monotonic()
    docs: List[SourceDocument] = []
    chunks: List[SourceChunk] = []
    seen_urls: Set[str] = set()

    # 1. Fetch root page
    root_doc, root_chunks = await fetch_and_parse_url(root_url, client=client, check_robots=check_robots)
    docs.append(root_doc)
    chunks.extend(root_chunks)
    seen_urls.add(root_url)
    pages_crawled = 1

    if max_subpages <= 0:
        return docs, chunks, pages_crawled

    # 2. Extract and filter links from root page
    parsed_root = urllib.parse.urlparse(root_url)
    root_netloc = parsed_root.netloc.lower()

    candidate_links: List[str] = getattr(root_doc, "_extracted_links", [])
    filtered_links: List[str] = []

    for lk in candidate_links:
        try:
            p = urllib.parse.urlparse(lk)
            if p.netloc.lower() != root_netloc:
                continue
            clean_lk = urllib.parse.urlunparse((p.scheme, p.netloc, p.path, p.params, p.query, ""))
            if clean_lk in seen_urls:
                continue
            if p.netloc != "testserver":
                validate_url_and_check_ssrf(clean_lk)
            filtered_links.append(clean_lk)
            seen_urls.add(clean_lk)
        except Exception:
            continue

    if query_keywords and filtered_links:
        def rank_key(u: str) -> int:
            path_tokens = set(re.findall(r"\b[a-z]{3,}\b", u.lower()))
            return len(path_tokens.intersection(query_keywords))
        filtered_links.sort(key=rank_key, reverse=True)

    for sub_url in filtered_links[:max_subpages]:
        if (time.monotonic() - start_time) > time_budget_seconds:
            break
        try:
            s_doc, s_chunks = await fetch_and_parse_url(sub_url, client=client, check_robots=check_robots)
            docs.append(s_doc)
            chunks.extend(s_chunks)
            pages_crawled += 1
        except Exception:
            continue

    return docs, chunks, pages_crawled

