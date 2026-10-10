"""
Tavily Web Evidence Provider.
Optional provider activated only when TAVILY_API_KEY is configured.
"""
from typing import List
import httpx

from backend.app.config import settings
from backend.app.services.web_evidence.base import WebEvidenceProvider, WebSearchResult
from backend.app.services.web_evidence.cache import web_cache

class TavilyProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "tavily"

    @property
    def origin_type(self) -> str:
        return "web_search"

    def is_available(self) -> bool:
        return bool(settings.TAVILY_API_KEY and settings.TAVILY_API_KEY.strip())

    async def search(self, query: str, max_results: int = 3) -> List[WebSearchResult]:
        if not self.is_available():
            return []

        query_clean = query.strip()
        if not query_clean:
            return []

        cached = web_cache.get(self.provider_name, query_clean)
        if cached is not None:
            return cached

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": query_clean,
            "search_depth": "basic",
            "max_results": max_results
        }

        results: List[WebSearchResult] = []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", []):
                        results.append(
                            WebSearchResult(
                                title=item.get("title", "Web Result"),
                                snippet=item.get("content", "")[:400],
                                url=item.get("url", ""),
                                source_name="Tavily Web Search",
                                origin_type=self.origin_type,
                                relevance_score=float(item.get("score", 0.75))
                            )
                        )
        except Exception:
            return []

        web_cache.set(self.provider_name, query_clean, results)
        return results
