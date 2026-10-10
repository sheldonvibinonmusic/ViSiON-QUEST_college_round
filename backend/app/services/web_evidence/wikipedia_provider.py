"""
Wikipedia Web Evidence Provider.
100% free and keyless using the official MediaWiki API with a descriptive User-Agent.
"""
import re
import urllib.parse
from typing import List
import httpx

from backend.app.services.web_evidence.base import WebEvidenceProvider, WebSearchResult
from backend.app.services.web_evidence.cache import web_cache

USER_AGENT = "SecondOpinionAuditor/1.0 (Evidence-Grounded AI Answer Auditor; mailto:auditor@secondopinion.local)"

class WikipediaProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "wikipedia"

    @property
    def origin_type(self) -> str:
        return "wikipedia"

    def is_available(self) -> bool:
        return True  # Keyless and always available

    async def search(self, query: str, max_results: int = 3) -> List[WebSearchResult]:
        query_clean = query.strip()
        if not query_clean:
            return []

        cached = web_cache.get(self.provider_name, query_clean)
        if cached is not None:
            return cached

        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query_clean,
            "utf8": "1",
            "format": "json",
            "srlimit": max_results,
        }
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }

        results: List[WebSearchResult] = []
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    search_items = data.get("query", {}).get("search", [])
                    for item in search_items:
                        title = item.get("title", "")
                        raw_snippet = item.get("snippet", "")
                        # Strip HTML formatting tags (e.g., <span class="searchmatch">)
                        clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
                        encoded_title = urllib.parse.quote(title.replace(" ", "_"))
                        page_url = f"https://en.wikipedia.org/wiki/{encoded_title}"

                        results.append(
                            WebSearchResult(
                                title=f"Wikipedia: {title}",
                                snippet=clean_snippet or f"Summary overview for {title}.",
                                url=page_url,
                                source_name="Wikipedia",
                                origin_type=self.origin_type,
                                relevance_score=0.85
                            )
                        )
        except Exception:
            # Network failure, timeout, or rate limiting; return empty list gracefully
            return []

        web_cache.set(self.provider_name, query_clean, results)
        return results
