"""
Tests for Cost Guard, Query Budgeting, and Privacy Sanitization.
Verifies checkability filtering, query caps, and privacy stripping.
"""
import pytest
from unittest.mock import patch, AsyncMock

from backend.app.services.cost_guard import (
    is_checkable_claim,
    sanitize_privacy_query,
    CostBudgetTracker,
)
from backend.app.services.audit_service import process_audit
from backend.app.services.web_evidence.base import WebSearchResult

def test_is_checkable_claim():
    # Factual assertions should be checkable
    factual = "Albert Einstein was awarded the Nobel Prize in Physics in 1921."
    is_ch, reason = is_checkable_claim(factual)
    assert is_ch is True

    # Politeness / conversational filler should NOT be checkable
    filler = "I hope this helps you understand the concept better!"
    is_ch, reason = is_checkable_claim(filler)
    assert is_ch is False
    assert "filler" in reason.lower()

    # Salutation should NOT be checkable
    greeting = "Hello and welcome to this explanation!"
    is_ch, reason = is_checkable_claim(greeting)
    assert is_ch is False

    # Question should NOT be checkable
    question = "Why does water expand when it freezes?"
    is_ch, reason = is_checkable_claim(question)
    assert is_ch is False
    assert "question" in reason.lower()

def test_sanitize_privacy_query():
    # Strips email, Windows path, and Unix path
    dirty_text = "Check user data from john.doe@example.com located at C:\\Users\\Admin\\data.txt and /var/log/syslog regarding thermodynamics."
    clean_query = sanitize_privacy_query(dirty_text, max_words=6)
    assert "john.doe@example.com" not in clean_query
    assert "C:\\Users" not in clean_query
    assert "/var/log" not in clean_query
    assert "thermodynamics" in clean_query
    assert len(clean_query.split()) <= 6

def test_cost_budget_tracker():
    tracker = CostBudgetTracker(max_queries=2)
    assert tracker.can_query() is True
    assert not tracker.is_budget_exhausted

    tracker.record_query()
    assert tracker.can_query() is True

    tracker.record_query()
    assert tracker.can_query() is False
    assert tracker.is_budget_exhausted

@pytest.mark.anyio
async def test_audit_skips_uncheckable_filler():
    """
    Verifies that conversational banter and questions in AI answers
    do not trigger external web search queries.
    """
    answer_with_banter = (
        "Hello! I hope this helps you.\n"
        "The speed of light in vacuum is approximately 299,792,458 meters per second.\n"
        "Let me know if you have any further questions!"
    )

    mock_results = [
        WebSearchResult(
            title="Speed of light",
            snippet="The speed of light in vacuum is defined as exactly 299,792,458 m/s.",
            url="https://en.wikipedia.org/wiki/Speed_of_light",
            source_name="Wikipedia",
            origin_type="wikipedia",
            relevance_score=0.95
        )
    ]

    with patch("backend.app.services.web_evidence.provider_chain.WebEvidenceChain.fetch_evidence_for_query", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_results

        response = await process_audit(
            answer=answer_with_banter,
            source_text=None,
            files=None,
            enable_web_search_flag=True
        )

        assert response.status_code if hasattr(response, "status_code") else True
        # Only the factual claim about the speed of light should have triggered a search
        # The greeting and conversational filler should have been skipped
        assert mock_fetch.call_count == 1
        called_query = mock_fetch.call_args[0][0]
        assert "speed" in called_query.lower() or "light" in called_query.lower()
        assert "hello" not in called_query.lower()
        assert "hope" not in called_query.lower()
