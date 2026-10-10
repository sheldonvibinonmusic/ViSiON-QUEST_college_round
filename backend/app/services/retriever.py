"""
BM25 Evidence Retrieval Service.
Indexes source chunks and retrieves candidate evidence passages for answer claims.
Uses BM25Plus to avoid negative IDF penalties on small or concise documents.
"""
import re
from typing import List, Tuple
from rank_bm25 import BM25Plus, BM25Okapi

from backend.app.schemas import SourceChunk, EvidenceReference
from backend.app.util.hashes import generate_id

def tokenize(text: str) -> List[str]:
    """
    Tokenize text into lowercase words, preserving numbers, percentages, and currency.
    e.g. '$500', '2026', 'employees'
    """
    return re.findall(r'\$?\d+(?:\.\d+)?%?|[a-zA-Z0-9_-]+', text.lower())

class BM25Retriever:
    def __init__(self, chunks: List[SourceChunk]):
        self.chunks = chunks
        self.tokenized_corpus = [tokenize(c.text) for c in chunks]
        # Use BM25Plus if available to prevent negative IDF on small document sets
        if self.tokenized_corpus and any(len(doc) > 0 for doc in self.tokenized_corpus):
            try:
                self.bm25 = BM25Plus(self.tokenized_corpus)
            except Exception:
                self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None

    def retrieve_candidates(
        self,
        query: str,
        source_name_map: dict = None,
        top_k: int = 3,
        min_overlap: int = 2
    ) -> List[EvidenceReference]:
        """
        Retrieve the top candidate chunks for a given query (claim).
        Returns EvidenceReference objects ordered by retrieval score.
        """
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        query_set = set(query_tokens)

        # Pair chunk, score, and token overlap
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        candidates: List[EvidenceReference] = []

        for rank, idx in enumerate(ranked_indices[:top_k], start=1):
            score = float(scores[idx])
            chunk_tokens = set(self.tokenized_corpus[idx])
            overlap = len(query_set.intersection(chunk_tokens))

            # Discard if zero overlap
            if overlap < min_overlap and score <= 0.0:
                continue

            chunk = self.chunks[idx]
            source_name = (source_name_map or {}).get(chunk.source_id, "Source Document")

            candidates.append(
                EvidenceReference(
                    evidence_id=generate_id("evi"),
                    source_id=chunk.source_id,
                    source_name=source_name,
                    quote=chunk.text,
                    page_number=chunk.page_number,
                    section=chunk.section,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    relation="candidate",
                    retrieval_rank=rank,
                )
            )

        return candidates
