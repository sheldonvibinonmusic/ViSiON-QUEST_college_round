"""
Serper (Google Search) Web Evidence Provider.
Optional provider activated only when SERPER_API_KEY is configured.
"""
from typing import List
import httpx

from backend.app.config import settings
from backend.app.services.web_evidence.base import WebEvidenceProvider, WebSearchResult
from backend.app.services.web_evidence.cache import web_cache

class SerperProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "serper"

    @property
    def origin_type(self) -> str:
        return "web_search"

    def is_available(self) -> bool:
        return bool(settings.SERPER_API_KEY and settings.SERPER_API_KEY.strip())

    async def search(self, query: str, max_results: int = 3) -> List[WebSearchResult]:
        if not self.is_available():
            return []

        query_clean = query.strip()
        if not query_clean:
            return []

        cached = web_cache.get(self.provider_name, query_clean)
        if cached is not None:
            return cached

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": settings.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query_clean,
            "num": max_results
        }

        results: List[WebSearchResult] = []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("organic", []):
                        results.append(
                            WebSearchResult(
                                title=item.get("title", "Web Result"),
                                snippet=item.get("snippet", "")[:400],
                                url=item.get("link", ""),
                                source_name="Google via Serper",
                                origin_type=self.origin_type,
                                relevance_score=0.75
                            )
                        )
        except Exception:
            return []

        web_cache.set(self.provider_name, query_clean, results)
        return results
