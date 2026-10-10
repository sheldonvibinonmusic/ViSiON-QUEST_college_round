"""
Tests for Web Evidence Layer, Keyless Providers, Cache, and No-Source Auditing Mode.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.errors import SecondOpinionException, ErrorCode
from backend.app.services.web_evidence.base import WebSearchResult
from backend.app.services.web_evidence.cache import InMemoryWebCache
from backend.app.services.web_evidence.provider_chain import (
    extract_safe_search_query,
    WebEvidenceChain,
)
from backend.app.services.web_evidence.wikipedia_provider import WikipediaProvider
from backend.app.services.audit_service import process_audit

client = TestClient(app)

def test_in_memory_web_cache():
    cache = InMemoryWebCache(max_items=2, ttl_seconds=1)
    res = [
        WebSearchResult(
            title="Test Title",
            snippet="Test Snippet",
            url="https://example.org",
            source_name="Example",
            origin_type="wikipedia"
        )
    ]

    cache.set("wiki", "quantum mechanics", res)
    assert cache.get("wiki", "quantum mechanics") is not None
    assert cache.get("wiki", "unknown query") is None

    # Capacity eviction
    cache.set("wiki", "relativity", res)
    cache.set("wiki", "thermodynamics", res)
    # oldest ("quantum mechanics") should be evicted
    assert cache.get("wiki", "quantum mechanics") is None
    assert cache.get("wiki", "relativity") is not None
    assert cache.get("wiki", "thermodynamics") is not None

def test_safe_query_extraction():
    long_claim = (
        "Albert Einstein published his famous paper on the photoelectric effect in 1905, "
        "which subsequently earned him the Nobel Prize in Physics."
    )
    query = extract_safe_search_query(long_claim, max_words=6)
    # Check word count is capped
    assert len(query.split()) <= 6
    assert "Albert" in query
    assert "Einstein" in query

@pytest.mark.anyio
async def test_wikipedia_provider_parsing():
    provider = WikipediaProvider()
    mock_payload = {
        "query": {
            "search": [
                {
                    "title": "General relativity",
                    "snippet": "General relativity is the <span class=\"searchmatch\">geometric</span> theory of gravitation.",
                    "pageid": 12345
                }
            ]
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        from unittest.mock import MagicMock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_payload
        mock_get.return_value = mock_resp

        results = await provider.search("general relativity", max_results=1)
        assert len(results) == 1
        assert results[0].title == "Wikipedia: General relativity"
        assert "<span" not in results[0].snippet  # HTML must be stripped
        assert "geometric theory of gravitation" in results[0].snippet
        assert results[0].url == "https://en.wikipedia.org/wiki/General_relativity"
        assert results[0].origin_type == "wikipedia"

@pytest.mark.anyio
async def test_no_source_web_mode_audit():
    """
    Core Product Requirement:
    When user has no local sources and enable_web_search is True,
    Second Opinion conducts an audit using free web evidence (Wikipedia/arXiv).
    """
    mock_results = [
        WebSearchResult(
            title="General relativity",
            snippet="General relativity is Einstein's geometric theory of gravitation, formulated in 1915.",
            url="https://en.wikipedia.org/wiki/General_relativity",
            source_name="Wikipedia",
            origin_type="wikipedia",
            relevance_score=0.9
        )
    ]

    with patch("backend.app.services.web_evidence.provider_chain.WebEvidenceChain.fetch_evidence_for_query", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_results

        response = await process_audit(
            answer="Albert Einstein formulated general relativity in 1915.",
            source_text=None,
            files=None,
            enable_web_search_flag=True
        )

        assert response.source_mode == "web_search"
        assert len(response.sources) > 0
        assert len(response.findings) > 0

        first_finding = response.findings[0]
        assert len(first_finding.evidence) > 0
        evi = first_finding.evidence[0]
        assert evi.origin_type == "wikipedia"
        assert evi.source_url == "https://en.wikipedia.org/wiki/General_relativity"
        assert first_finding.independent_sources_agreeing >= 1

@pytest.mark.anyio
async def test_no_source_mode_fails_when_web_search_disabled():
    """
    Backward Compatibility:
    Submitting an audit without sources and with web search disabled must raise SOURCE_EMPTY_OR_UNREADABLE.
    """
    with pytest.raises(SecondOpinionException) as exc_info:
        await process_audit(
            answer="This answer has no reference source provided.",
            source_text=None,
            files=None,
            enable_web_search_flag=False
        )

    assert exc_info.value.detail["code"] == ErrorCode.SOURCE_EMPTY_OR_UNREADABLE.value

def test_api_audit_with_enable_web_search():
    """
    Verify POST /api/audits route accepts enable_web_search and executes no-source auditing.
    """
    mock_results = [
        WebSearchResult(
            title="Photosynthesis",
            snippet="Photosynthesis is a process used by plants to convert light energy into chemical energy.",
            url="https://en.wikipedia.org/wiki/Photosynthesis",
            source_name="Wikipedia",
            origin_type="wikipedia",
            relevance_score=0.9
        )
    ]

    with patch("backend.app.services.web_evidence.provider_chain.WebEvidenceChain.fetch_evidence_for_query", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_results

        response = client.post(
            "/api/audits",
            data={
                "answer": "Plants use photosynthesis to convert sunlight into energy.",
                "enable_web_search": "true"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["source_mode"] == "web_search"
        assert len(data["findings"]) > 0
        assert data["findings"][0]["evidence"][0]["origin_type"] == "wikipedia"
