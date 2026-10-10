"""
Base classes and contracts for Web Evidence Providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class WebSearchResult(BaseModel):
    title: str
    snippet: str
    url: str
    source_name: str
    origin_type: str  # "wikipedia", "scholarly_arxiv", "scholarly_crossref", "tavily", "serper"
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    relevance_score: float = 0.0

class WebEvidenceProvider(ABC):
    """
    Abstract interface for search and retrieval providers.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def origin_type(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider can be queried (e.g. keyless or required keys configured)."""
        pass

    @abstractmethod
    async def search(self, query: str, max_results: int = 3) -> List[WebSearchResult]:
        """Perform search query and return formatted WebSearchResult items."""
        pass
