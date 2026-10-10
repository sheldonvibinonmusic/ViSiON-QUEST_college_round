"""
In-memory transient TTL cache for web search queries.
Complies with zero-persistence policy: no SQLite or disk writes; auto-eviction on capacity and TTL.
"""
import time
from typing import Dict, List, Tuple, Optional
from collections import OrderedDict
from backend.app.config import settings
from backend.app.services.web_evidence.base import WebSearchResult

class InMemoryWebCache:
    """
    LRU + TTL in-memory cache for search results.
    """
    def __init__(self, max_items: int = 500, ttl_seconds: Optional[int] = None):
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds or settings.WEB_CACHE_TTL_SECONDS
        self._cache: OrderedDict[Tuple[str, str], Tuple[float, List[WebSearchResult]]] = OrderedDict()

    def _normalize_query(self, query: str) -> str:
        return " ".join(query.strip().lower().split())

    def get(self, provider_name: str, query: str) -> Optional[List[WebSearchResult]]:
        key = (provider_name, self._normalize_query(query))
        if key not in self._cache:
            return None

        cached_time, results = self._cache[key]
        if time.time() - cached_time > self.ttl_seconds:
            # Expired
            del self._cache[key]
            return None

        # Move to end (MRU)
        self._cache.move_to_end(key)
        return results

    def set(self, provider_name: str, query: str, results: List[WebSearchResult]) -> None:
        key = (provider_name, self._normalize_query(query))
        now = time.time()

        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (now, results)

        # Evict oldest if exceeding max_items
        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)

# Global in-memory cache instance
web_cache = InMemoryWebCache()
