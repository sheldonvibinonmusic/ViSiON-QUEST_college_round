"""
Provider Chain & Query Orchestrator for Web Evidence.
Manages provider fallbacks (Wikipedia -> arXiv -> Crossref -> optional search APIs),
enforces privacy constraints (short query extraction only), and converts search results into
auditable SourceDocument and SourceChunk entities.
"""
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.schemas import SourceDocument, SourceChunk
from backend.app.util.hashes import generate_id, compute_sha256
from backend.app.services.web_evidence.base import WebSearchResult, WebEvidenceProvider
from backend.app.services.web_evidence.wikipedia_provider import WikipediaProvider
from backend.app.services.web_evidence.scholarly_provider import ArxivProvider, CrossrefProvider
from backend.app.services.web_evidence.tavily_provider import TavilyProvider
from backend.app.services.web_evidence.serper_provider import SerperProvider

from backend.app.services.cost_guard import sanitize_privacy_query

ACADEMIC_KEYWORDS = {
    "theorem", "hypothesis", "quantum", "physics", "relativity", "algorithm",
    "mechanics", "biology", "molecular", "enzyme", "chemical", "equation",
    "astrophysics", "experiment", "proof", "mathematical", "thermodynamics"
}

def extract_safe_search_query(text: str, max_words: int = 10) -> str:
    """
    Extract a concise, privacy-safe query from claim text using cost_guard sanitization.
    Never sends full documents, local file paths, or PII to external web providers.
    """
    return sanitize_privacy_query(text, max_words=max_words)

class WebEvidenceChain:
    """
    Orchestrates web evidence retrieval across keyless and optional providers.
    """
    def __init__(self):
        self.wikipedia = WikipediaProvider()
        self.arxiv = ArxivProvider()
        self.crossref = CrossrefProvider()
        self.tavily = TavilyProvider()
        self.serper = SerperProvider()

    def _is_scholarly(self, query: str) -> bool:
        lower = query.lower()
        return any(kw in lower for kw in ACADEMIC_KEYWORDS)

    async def fetch_evidence_for_query(
        self,
        query: str,
        max_results: int = 3
    ) -> List[WebSearchResult]:
        """
        Query chain with smart routing and keyless fallback.
        """
        safe_query = extract_safe_search_query(query)
        if not safe_query:
            return []

        all_results: List[WebSearchResult] = []
        seen_urls = set()

        # Route 1: Scholarly queries check arXiv or Crossref
        if self._is_scholarly(safe_query):
            try:
                scholarly_results = await self.arxiv.search(safe_query, max_results=2)
            except Exception:
                scholarly_results = []
            if not scholarly_results:
                try:
                    scholarly_results = await self.crossref.search(safe_query, max_results=2)
                except Exception:
                    scholarly_results = []
            for res in scholarly_results:
                if res.url not in seen_urls:
                    seen_urls.add(res.url)
                    all_results.append(res)

        # Route 2: Wikipedia (Keyless, fast, high authority)
        try:
            wiki_results = await self.wikipedia.search(safe_query, max_results=max_results)
        except Exception:
            wiki_results = []
        for res in wiki_results:
            if res.url not in seen_urls:
                seen_urls.add(res.url)
                all_results.append(res)

        # Route 3: Optional providers (Tavily / Serper) if configured and results are few
        if len(all_results) < max_results:
            if self.tavily.is_available():
                try:
                    tav_results = await self.tavily.search(safe_query, max_results=max_results - len(all_results))
                except Exception:
                    tav_results = []
                for res in tav_results:
                    if res.url not in seen_urls:
                        seen_urls.add(res.url)
                        all_results.append(res)

            elif self.serper.is_available():
                try:
                    serp_results = await self.serper.search(safe_query, max_results=max_results - len(all_results))
                except Exception:
                    serp_results = []
                for res in serp_results:
                    if res.url not in seen_urls:
                        seen_urls.add(res.url)
                        all_results.append(res)

        return all_results[:max_results]

    def convert_results_to_sources(
        self,
        results: List[WebSearchResult]
    ) -> Tuple[List[SourceDocument], List[SourceChunk], Dict[str, WebSearchResult]]:
        """
        Convert WebSearchResults into native SourceDocuments and SourceChunks.
        Returns (source_documents, source_chunks, chunk_id_to_result_map).
        """
        docs: List[SourceDocument] = []
        chunks: List[SourceChunk] = []
        chunk_map: Dict[str, WebSearchResult] = {}

        for res in results:
            content_bytes = (res.title + "\n" + res.snippet).encode("utf-8")
            sha = compute_sha256(content_bytes)
            source_id = generate_id("src_web")

            doc = SourceDocument(
                source_id=source_id,
                filename=f"{res.source_name}: {res.title[:40]}",
                media_type="text/plain",
                sha256=sha,
                character_count=len(res.snippet),
                page_count=1,
                extraction_status="success",
                warnings=[]
            )
            docs.append(doc)

            chunk_id = generate_id("chk_web")
            chunk = SourceChunk(
                chunk_id=chunk_id,
                source_id=source_id,
                text=res.snippet,
                start_char=0,
                end_char=len(res.snippet),
                page_number=1,
                section=res.title,
                retrieval_score=res.relevance_score
            )
            chunks.append(chunk)
            chunk_map[chunk_id] = res

        return docs, chunks, chunk_map

web_evidence_chain = WebEvidenceChain()
