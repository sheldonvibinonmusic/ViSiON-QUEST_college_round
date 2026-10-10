"""
Tests for BM25 Evidence Retrieval Service.
"""
from pathlib import Path
from backend.app.services.document_parser import parse_plain_text
from backend.app.services.source_chunks import chunk_document
from backend.app.services.retriever import BM25Retriever, tokenize

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_tokenize_preserves_numbers_and_currency():
    tokens = tokenize("Employees receive up to $500 for equipment by 2026.")
    assert "$500" in tokens
    assert "2026" in tokens
    assert "employees" in tokens

def test_retriever_ranking_on_policy_document():
    policy_text = (FIXTURES_DIR / "sample_policy.txt").read_text(encoding="utf-8")
    parsed = parse_plain_text(policy_text, "sample_policy.txt")
    chunks = chunk_document(parsed, target_words=50, overlap_words=10)
    
    retriever = BM25Retriever(chunks)
    candidates = retriever.retrieve_candidates(
        query="home office equipment reimbursement of up to $500",
        top_k=2
    )

    assert len(candidates) > 0
    top_candidate = candidates[0]
    assert top_candidate.retrieval_rank == 1
    assert "$500" in top_candidate.quote
    assert "reimbursement" in top_candidate.quote.lower()

def test_empty_corpus_and_empty_query():
    retriever = BM25Retriever([])
    candidates = retriever.retrieve_candidates("test query")
    assert candidates == []

    # Non-empty retriever with empty query
    policy_text = (FIXTURES_DIR / "sample_policy.txt").read_text(encoding="utf-8")
    parsed = parse_plain_text(policy_text, "sample_policy.txt")
    chunks = chunk_document(parsed)
    retriever_loaded = BM25Retriever(chunks)
    assert retriever_loaded.retrieve_candidates("") == []
    assert retriever_loaded.retrieve_candidates("   ") == []
