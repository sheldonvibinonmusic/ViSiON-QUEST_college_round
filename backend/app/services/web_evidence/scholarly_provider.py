"""
Scholarly Web Evidence Providers (arXiv and Crossref).
100% free and keyless scholarly document retrieval.
"""
import re
import xml.etree.ElementTree as ET
from typing import List
import httpx

from backend.app.config import settings
from backend.app.services.web_evidence.base import WebEvidenceProvider, WebSearchResult
from backend.app.services.web_evidence.cache import web_cache

USER_AGENT = f"SecondOpinionAuditor/1.0 (Scholarly Auditor; mailto:{settings.CROSSREF_MAILTO})"

class ArxivProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "arxiv"

    @property
    def origin_type(self) -> str:
        return "scholarly_arxiv"

    def is_available(self) -> bool:
        return True  # Keyless

    async def search(self, query: str, max_results: int = 3) -> List[WebSearchResult]:
        query_clean = query.strip()
        if not query_clean:
            return []

        cached = web_cache.get(self.provider_name, query_clean)
        if cached is not None:
            return cached

        url = "https://export.arxiv.org/api/query"
        # Sanitize query for arXiv query format
        search_terms = "+AND+".join(re.findall(r"\b[A-Za-z0-9_-]{3,}\b", query_clean)[:6])
        if not search_terms:
            return []

        params = {
            "search_query": f"all:{search_terms}",
            "start": "0",
            "max_results": str(max_results)
        }
        headers = {"User-Agent": USER_AGENT}

        results: List[WebSearchResult] = []
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.text)
                    atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
                    entries = root.findall("atom:entry", atom_ns)
                    for entry in entries:
                        title_el = entry.find("atom:title", atom_ns)
                        summary_el = entry.find("atom:summary", atom_ns)
                        id_el = entry.find("atom:id", atom_ns)

                        title = " ".join(title_el.text.split()) if title_el is not None and title_el.text else "Untitled Paper"
                        summary = " ".join(summary_el.text.split()) if summary_el is not None and summary_el.text else ""
                        paper_url = id_el.text.strip() if id_el is not None and id_el.text else "https://arxiv.org"

                        results.append(
                            WebSearchResult(
                                title=f"arXiv: {title}",
                                snippet=summary[:400] if summary else f"arXiv paper: {title}",
                                url=paper_url,
                                source_name="arXiv",
                                origin_type=self.origin_type,
                                relevance_score=0.88
                            )
                        )
        except Exception:
            return []

        web_cache.set(self.provider_name, query_clean, results)
        return results

class CrossrefProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "crossref"

    @property
    def origin_type(self) -> str:
        return "scholarly_crossref"

    def is_available(self) -> bool:
        return True  # Keyless polite pool

    async def search(self, query: str, max_results: int = 3) -> List[WebSearchResult]:
        query_clean = query.strip()
        if not query_clean:
            return []

        cached = web_cache.get(self.provider_name, query_clean)
        if cached is not None:
            return cached

        url = "https://api.crossref.org/works"
        params = {
            "query": query_clean,
            "rows": str(max_results),
            "mailto": settings.CROSSREF_MAILTO
        }
        headers = {"User-Agent": USER_AGENT}

        results: List[WebSearchResult] = []
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("message", {}).get("items", [])
                    for item in items:
                        titles = item.get("title", [])
                        title = titles[0] if titles else "Scholarly Publication"
                        doi_url = item.get("URL", f"https://doi.org/{item.get('DOI', '')}")
                        container = item.get("container-title", [])
                        publisher = item.get("publisher", "")
                        abstract = item.get("abstract", "")
                        # Strip XML tags from Crossref abstract (e.g. <jats:p>)
                        clean_abstract = re.sub(r"<[^>]+>", "", abstract).strip() if abstract else ""

                        venue = container[0] if container else publisher
                        snippet = clean_abstract[:400] if clean_abstract else f"Published in {venue}. Title: {title}"

                        results.append(
                            WebSearchResult(
                                title=f"Crossref: {title}",
                                snippet=snippet,
                                url=doi_url,
                                source_name="Crossref",
                                origin_type=self.origin_type,
                                relevance_score=0.80
                            )
                        )
        except Exception:
            return []

        web_cache.set(self.provider_name, query_clean, results)
        return results
