"""
Phase 2 Part C: Pipeline-Level Stress and Resiliency Test Suite.
Verifies all 15 pipeline edge cases specified in the test plan:
1. Physics answer with maths source (domain mismatch)
2. Maths answer with physics source (domain mismatch)
3. Relevant source (supported)
4. Partly relevant source
5. Contradicting source
6. No source (web mode)
7. Mixed mode (local doc + web search fallback)
8. Two sources where one is off-topic
9. Single provider failure (fallback succeeds)
10. All providers failing (clean engine warning)
11. Malformed or empty URL list
12. Many URLs at once (>5 URLs error)
13. Same URL twice (deduplicated)
14. Concurrent requests (asyncio.gather)
15. Audit timeout partway returning status='incomplete'
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.app.schemas import (
    AuditResponse,
    FactualVerdict,
    SourceFitLevel,
)
from backend.app.services.web_evidence.base import WebEvidenceProvider, WebSearchResult
from backend.app.services.audit_service import process_audit
from backend.app.errors import SecondOpinionException, ErrorCode
from backend.app.services.web_evidence.provider_chain import WebEvidenceChain

# ==============================================================================
# 1 & 2. DOMAIN MISMATCH (Cases 1 & 2)
# ==============================================================================

@pytest.mark.anyio
async def test_case_1_physics_answer_maths_source_mismatch():
    """Case 1: Physics answer evaluated against purely algebraic maths source."""
    answer = "Electrons orbit the atomic nucleus in quantum probability clouds governed by the wave function."
    source = "In abstract algebra, a group is a mathematical structure consisting of a set with an associative binary operation, an identity element, and inverse elements."

    res = await process_audit(
        answer=answer,
        source_text=source,
        check_source_fit_flag=True,
    )

    assert res.source_fit is not None
    assert res.source_fit.all_sources_off_topic is True
    assert res.source_fit.overall_fit == SourceFitLevel.OFF_TOPIC
    assert len(res.findings) > 0
    # Must be NOT_ESTABLISHED due to domain mismatch, never false contradiction
    assert res.findings[0].verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
    assert "domain mismatch" in res.findings[0].explanation.lower() or "off-topic" in res.findings[0].explanation.lower()

@pytest.mark.anyio
async def test_case_2_maths_answer_physics_source_mismatch():
    """Case 2: Maths answer evaluated against purely thermodynamics physics source."""
    answer = "Every finite abelian group is isomorphic to a direct product of cyclic groups of prime-power order."
    source = "Thermodynamics studies heat transfer, entropy changes, molecular kinetics, and thermodynamic cycles in ideal gases."

    res = await process_audit(
        answer=answer,
        source_text=source,
        check_source_fit_flag=True,
    )

    assert res.source_fit is not None
    assert res.source_fit.all_sources_off_topic is True
    assert res.findings[0].verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE

# ==============================================================================
# 3, 4, 5. RELEVANT, PARTLY RELEVANT, CONTRADICTING (Cases 3, 4, 5)
# ==============================================================================

@pytest.mark.anyio
async def test_case_3_relevant_source():
    """Case 3: Fully relevant source directly supporting the claim."""
    answer = "Water boils at 100 degrees Celsius at standard atmospheric pressure."
    source = "Under standard atmospheric pressure of 1 atm, pure water boils at 100 degrees Celsius."

    res = await process_audit(
        answer=answer,
        source_text=source,
        check_source_fit_flag=True,
    )

    assert res.source_fit is not None
    assert res.source_fit.overall_fit == SourceFitLevel.RELEVANT
    assert res.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE
    assert res.summary.supported_claims >= 1

@pytest.mark.anyio
async def test_case_4_partly_relevant_source():
    """Case 4: Partly relevant source covering some aspects but missing others."""
    answer = "Chlorophyll pigments absorb sunlight energy during photosynthesis in plant cells."
    source = "Plant cells utilize chlorophyll pigments to capture visible sunlight."

    res = await process_audit(
        answer=answer,
        source_text=source,
        check_source_fit_flag=True,
    )

    assert res.source_fit is not None
    assert res.source_fit.overall_fit in (SourceFitLevel.RELEVANT, SourceFitLevel.PARTIALLY_RELEVANT)
    assert res.findings[0].verdict in (FactualVerdict.SUPPORTED_BY_SOURCE, FactualVerdict.NOT_ESTABLISHED_BY_SOURCE)

@pytest.mark.anyio
async def test_case_5_contradicting_source():
    """Case 5: Contradicting source directly refuting the claim."""
    answer = "Albert Einstein formulated the general theory of relativity in 1950."
    source = "Albert Einstein completed his general theory of relativity in 1915."

    res = await process_audit(
        answer=answer,
        source_text=source,
    )

    assert len(res.findings) > 0
    assert res.findings[0].verdict == FactualVerdict.CONTRADICTED_BY_SOURCE
    assert res.summary.contradicted_claims >= 1

# ==============================================================================
# 6 & 7. NO SOURCE & MIXED MODE (Cases 6 & 7)
# ==============================================================================

@pytest.mark.anyio
async def test_case_6_no_source_web_mode():
    """Case 6: No local sources provided, web search enabled."""
    mock_item = WebSearchResult(
        title="Speed of light",
        snippet="The speed of light in vacuum is precisely 299,792,458 metres per second.",
        url="https://en.wikipedia.org/wiki/Speed_of_light",
        source_name="Wikipedia",
        origin_type="wikipedia",
    )
    with patch("backend.app.services.web_evidence.provider_chain.WebEvidenceChain.fetch_evidence_for_query", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [mock_item]

        res = await process_audit(
            answer="The speed of light in vacuum is 299,792,458 metres per second.",
            source_text=None,
            files=None,
            enable_web_search_flag=True,
        )

        assert res.source_mode == "web_search"
        assert len(res.sources) > 0
        assert res.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE
        assert res.findings[0].evidence[0].origin_type == "wikipedia"

@pytest.mark.anyio
async def test_case_7_mixed_mode():
    """Case 7: Local document is off-topic, triggers fallback web evidence retrieval."""
    local_source = "Cooking recipes for Italian pasta and garlic bread."
    mock_item = WebSearchResult(
        title="DNA Structure",
        snippet="DNA is a double helix composed of adenine, thymine, cytosine, and guanine.",
        url="https://en.wikipedia.org/wiki/DNA",
        source_name="Wikipedia",
        origin_type="wikipedia",
    )
    with patch("backend.app.services.web_evidence.provider_chain.WebEvidenceChain.fetch_evidence_for_query", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [mock_item]

        res = await process_audit(
            answer="DNA is structured as a double helix composed of four nucleotides.",
            source_text=local_source,
            check_source_fit_flag=True,
            enable_web_search_flag=True,
        )

        assert res.source_mode == "mixed"
        assert len(res.sources) >= 2  # Local doc + Web doc

# ==============================================================================
# 8. TWO SOURCES WHERE ONE IS OFF-TOPIC (Case 8)
# ==============================================================================

@pytest.mark.anyio
async def test_case_8_two_sources_one_off_topic():
    """Case 8: One relevant source and one off-topic source provided together."""
    answer = "Jupiter is orbited by the Galilean moons Ganymede and Europa."
    source_relevant = "Jupiter has four large Galilean satellites named Io, Europa, Ganymede, and Callisto."
    source_irrelevant = "The French Revolution commenced in 1789 with the storming of the Bastille."
    combined_source = f"{source_relevant}\n\n=== Document Separator ===\n\n{source_irrelevant}"

    res = await process_audit(
        answer=answer,
        source_text=combined_source,
        check_source_fit_flag=True,
    )

    # Since at least one document segment covers Jupiter, all_sources_off_topic must be False
    assert res.source_fit is not None
    assert res.source_fit.all_sources_off_topic is False
    assert res.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE

# ==============================================================================
# 9 & 10. PROVIDER RESILIENCY (Cases 9 & 10)
# ==============================================================================

class FailingProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "FailingProvider"

    @property
    def origin_type(self) -> str:
        return "web_search"

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, max_results: int = 3):
        raise RuntimeError("Remote API connection timeout / 503 Service Unavailable")

class SuccessfulProvider(WebEvidenceProvider):
    @property
    def provider_name(self) -> str:
        return "BackupService"

    @property
    def origin_type(self) -> str:
        return "web_search"

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, max_results: int = 3):
        return [
            WebSearchResult(
                title="Backup Provider Result",
                snippet="Backup evidence verifying the query.",
                url="https://backup.example.org/evidence",
                source_name="BackupService",
                origin_type="web_search",
            )
        ]

@pytest.mark.anyio
async def test_case_9_single_provider_failure_fallback_succeeds():
    """Case 9: First provider throws exception, fallback provider succeeds."""
    chain = WebEvidenceChain()
    chain.arxiv = FailingProvider()
    chain.crossref = FailingProvider()
    chain.wikipedia = SuccessfulProvider()

    results = await chain.fetch_evidence_for_query("quantum computing theorem", max_results=2)
    assert len(results) == 1
    assert results[0].source_name == "BackupService"

@pytest.mark.anyio
async def test_case_10_all_providers_failing_clean_warning():
    """Case 10: All providers throw errors; returns empty list without crashing."""
    chain = WebEvidenceChain()
    chain.arxiv = FailingProvider()
    chain.crossref = FailingProvider()
    chain.wikipedia = FailingProvider()

    results = await chain.fetch_evidence_for_query("quantum computing theorem", max_results=2)
    assert results == []

# ==============================================================================
# 11, 12, 13. URL INPUT STRESS (Cases 11, 12, 13)
# ==============================================================================

@pytest.mark.anyio
async def test_case_11_malformed_or_empty_url_list():
    """Case 11: Empty/whitespace URL strings with no other sources raise SOURCE_EMPTY_OR_UNREADABLE."""
    with pytest.raises(SecondOpinionException) as exc_info:
        await process_audit(
            answer="Some answer claim.",
            urls="   \n  ,  , \t  ",
            source_text=None,
            files=None,
        )
    assert exc_info.value.detail["code"] == ErrorCode.SOURCE_EMPTY_OR_UNREADABLE.value

@pytest.mark.anyio
async def test_case_12_too_many_urls_rejected():
    """Case 12: Submitting more than 5 URLs raises INVALID_INPUT."""
    six_urls = (
        "https://site1.example.com, https://site2.example.com, "
        "https://site3.example.com, https://site4.example.com, "
        "https://site5.example.com, https://site6.example.com"
    )
    with pytest.raises(SecondOpinionException) as exc_info:
        await process_audit(
            answer="Some answer claim.",
            urls=six_urls,
        )
    assert exc_info.value.detail["code"] == ErrorCode.INVALID_INPUT.value
    assert "exceeds the limit of 5" in exc_info.value.detail["message"]

@pytest.mark.anyio
async def test_case_13_duplicate_urls_deduplicated():
    """Case 13: Submitting duplicate URLs deduplicates and records warning."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"<html><head><title>Test Page</title></head><body><p>This is a sufficiently long factual passage that provides genuine reference text for testing.</p></body></html>"

    with patch("backend.app.services.url_fetcher.validate_url_and_check_ssrf"):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            res = await process_audit(
                answer="Fact passage.",
                urls="https://example.com/page, https://example.com/page",
            )
            # Only one document ingested
            assert len(res.sources) == 1
            assert any("deduplicated" in w.lower() for w in res.warnings)

# ==============================================================================
# 14. CONCURRENT REQUESTS (Case 14)
# ==============================================================================

@pytest.mark.anyio
async def test_case_14_concurrent_requests():
    """Case 14: Multiple concurrent audit requests run without race conditions."""
    async def run_single(claim_text: str, fact_text: str):
        return await process_audit(
            answer=claim_text,
            source_text=fact_text,
        )

    tasks = [
        run_single("The sky appears blue due to Rayleigh scattering.", "Rayleigh scattering causes the sky to appear blue."),
        run_single("Helium is lighter than air.", "Helium has lower density than atmospheric air."),
        run_single("Gold is a noble metal.", "Gold resists oxidation and is categorized as a noble metal."),
        run_single("Mars has two small moons.", "Mars has two small natural satellites."),
    ]

    responses = await asyncio.gather(*tasks)
    assert len(responses) == 4
    for r in responses:
        assert isinstance(r, AuditResponse)
        assert r.status == "completed"
        assert len(r.findings) > 0
        assert r.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE

# ==============================================================================
# 15. TIMEOUT PARTWAY RETURNING INCOMPLETE (Case 15)
# ==============================================================================

@pytest.mark.anyio
async def test_case_15_audit_timeout_partway_incomplete_status():
    """Case 15: An audit that times out partway returns status='incomplete' with partial findings."""
    long_answer = (
        "Claim one: Water freezes at zero degrees Celsius. "
        "Claim two: Water boils at one hundred degrees Celsius. "
        "Claim three: Ice floats on liquid water. "
        "Claim four: Steam is water in gaseous form. "
        "Claim five: Heavy water contains deuterium."
    )
    source = "Water freezes at 0C and boils at 100C. Ice floats on water."

    # Force a near-zero timeout (e.g. 0.000001 seconds) during claim evaluation
    res = await process_audit(
        answer=long_answer,
        source_text=source,
        max_audit_seconds=0.000001,
    )

    assert res.status == "incomplete"
    assert any("time limit" in w.lower() or "partial" in w.lower() for w in res.warnings)
