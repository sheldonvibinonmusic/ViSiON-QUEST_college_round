"""
Evaluation Benchmark Test Suite (20 Labelled Cases).
Directly fulfills PROJECT_CONTEXT.md requirement (§3.2, Line 70):
"Pass an end-to-end test and a small labelled test set before performance claims are made."
Covers:
1. Supported factual claims (Science, History, Biology)
2. Numerical, date, and polarity contradictions
3. Domain mismatches (Physics/Baking, Math/Gardening, CS/Culinary) -> zero false contradictions
4. Insufficient evidence and ambiguous/conflicting passages
5. Citation support verification (date/entity integrity)
6. Strict SSRF defenses (loopback, metadata, invalid schemes)
7. Valid web URL ingestion with provenance
8. No-source web evidence mode
9. Cost guard checkability filtering and query caps
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from backend.app.schemas import FactualVerdict, SourceFitLevel, Claim, EvidenceReference
from backend.app.services.verdict_mapper import map_verdict_for_claim
from backend.app.errors import SecondOpinionException, ErrorCode
from backend.app.services.url_fetcher import validate_url_and_check_ssrf
from backend.app.services.cost_guard import is_checkable_claim, CostBudgetTracker
from backend.app.services.citation_checker import verify_citation_support
from backend.app.services.audit_service import process_audit
from backend.app.services.web_evidence.base import WebSearchResult

# ==============================================================================
# 1. DIRECT FACTUAL SUPPORT (Cases 1 - 3)
# ==============================================================================

@pytest.mark.anyio
async def test_case_01_support_biology():
    """Case 1: Direct Support - Biology (Cellular respiration)"""
    answer = "Mitochondria generate most of the chemical energy needed by the cell through ATP synthesis."
    source = "The mitochondria generate most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE
    assert res.findings[0].evidence[0].citation_verified is True
    assert res.findings[0].independent_sources_agreeing >= 1

@pytest.mark.anyio
async def test_case_02_support_physics():
    """Case 2: Direct Support - Physics (Speed of light)"""
    answer = "The speed of light in vacuum is defined as 299,792,458 meters per second."
    source = "By international agreement, the speed of light in vacuum is exactly 299,792,458 meters per second."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE
    assert res.findings[0].evidence[0].citation_verified is True

@pytest.mark.anyio
async def test_case_03_support_history():
    """Case 3: Direct Support - History (Magna Carta)"""
    answer = "King John of England granted the Magna Carta at Runnymede in 1215."
    source = "In June 1215 at Runnymede, King John of England granted the charter of rights known as Magna Carta."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE
    assert res.findings[0].evidence[0].citation_verified is True


# ==============================================================================
# 2. FACTUAL CONTRADICTIONS (Cases 4 - 6)
# ==============================================================================

@pytest.mark.anyio
async def test_case_04_contradiction_numerical():
    """Case 4: Contradiction - Numerical value discrepancy"""
    answer = "At standard sea-level pressure, pure water boils at 120 degrees Celsius."
    source = "Under standard atmospheric pressure at sea level, pure water boils at 100 degrees Celsius."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.CONTRADICTED_BY_SOURCE
    assert "Numerical discrepancy" in res.findings[0].explanation or "contradicts" in res.findings[0].explanation.lower()

@pytest.mark.anyio
async def test_case_05_contradiction_date():
    """Case 5: Contradiction - Year discrepancy"""
    answer = "Albert Einstein formulated the general theory of relativity in 1950."
    source = "Albert Einstein completed his general theory of relativity in 1915."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.CONTRADICTED_BY_SOURCE
    assert "Date discrepancy" in res.findings[0].explanation or "contradicts" in res.findings[0].explanation.lower()

@pytest.mark.anyio
async def test_case_06_contradiction_polarity():
    """Case 6: Contradiction - Polarity / negation inversion"""
    answer = "Employees can purchase their own laptops and request reimbursement."
    source = "Laptops are provided directly by IT and cannot be purchased for reimbursement."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.CONTRADICTED_BY_SOURCE
    assert "Polarity clash" in res.findings[0].explanation or "contradicts" in res.findings[0].explanation.lower()


# ==============================================================================
# 3. DOMAIN MISMATCH DEFENSE (Cases 7 - 9: Zero False Contradictions)
# ==============================================================================

@pytest.mark.anyio
async def test_case_07_domain_mismatch_physics_vs_baking():
    """Case 7: Domain Mismatch - Physics answer paired with baking recipe"""
    physics_answer = "Gravitational waves propagate through spacetime at exactly the speed of light."
    baking_source = "Fold the sourdough loaf gently and bake in a preheated Dutch oven for 30 minutes."
    res = await process_audit(answer=physics_answer, source_text=baking_source, check_source_fit_flag=True)
    assert res.source_fit.all_sources_off_topic is True
    assert res.source_fit.overall_fit == SourceFitLevel.OFF_TOPIC
    # MUST NOT be marked contradicted
    assert res.findings[0].verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
    assert "Source does not cover this topic" in res.findings[0].explanation

@pytest.mark.anyio
async def test_case_08_domain_mismatch_math_vs_gardening():
    """Case 8: Domain Mismatch - Mathematics answer paired with gardening instructions"""
    math_answer = "The Riemann hypothesis asserts that all non-trivial zeros of the zeta function have real part 1/2."
    gardening_source = "Prune dead shrub branches in early spring and ensure proper soil drainage for perennials."
    res = await process_audit(answer=math_answer, source_text=gardening_source, check_source_fit_flag=True)
    assert res.source_fit.all_sources_off_topic is True
    assert res.findings[0].verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE

@pytest.mark.anyio
async def test_case_09_domain_mismatch_cs_vs_culinary():
    """Case 9: Domain Mismatch - Computer science answer paired with culinary recipe"""
    cs_answer = "Dijkstra's algorithm calculates the shortest path in a weighted graph with non-negative edge weights."
    culinary_source = "Whisk the egg yolks with sugar until pale and creamy, then slowly incorporate warm milk."
    res = await process_audit(answer=cs_answer, source_text=culinary_source, check_source_fit_flag=True)
    assert res.source_fit.all_sources_off_topic is True
    assert res.findings[0].verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE


# ==============================================================================
# 4. INSUFFICIENT EVIDENCE & CONFLICTING EVIDENCE (Cases 10 - 11)
# ==============================================================================

@pytest.mark.anyio
async def test_case_10_insufficient_evidence():
    """Case 10: Insufficient Evidence - Related domain but specific claim detail missing"""
    answer = "The treaty included an unwritten secret annex concerning naval disarmament."
    source = "The diplomatic treaty established peaceful borders and commercial shipping tariffs between both nations."
    res = await process_audit(answer=answer, source_text=source)
    assert res.findings[0].verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
    assert "do not sufficiently establish" in res.findings[0].explanation

def test_case_11_ambiguous_conflicting_evidence():
    """Case 11: Ambiguous Evidence - Conflicting passages within sources"""
    claim = Claim(
        claim_id="clm_conflict",
        text="Remote employees are eligible for full health insurance benefits.",
        start_char=0,
        end_char=65,
        parent_sentence="Remote employees are eligible for full health insurance benefits."
    )
    evi1 = EvidenceReference(
        evidence_id="evi_1",
        source_id="src_1",
        source_name="Policy A",
        quote="Remote employees are eligible for full health insurance benefits.",
        start_char=0,
        end_char=65,
        relation="candidate",
        retrieval_rank=1
    )
    evi2 = EvidenceReference(
        evidence_id="evi_2",
        source_id="src_2",
        source_name="Policy B",
        quote="Remote employees are not eligible for health insurance benefits under any circumstances.",
        start_char=0,
        end_char=88,
        relation="candidate",
        retrieval_rank=2
    )
    finding = map_verdict_for_claim(claim, [evi1, evi2])
    assert finding.verdict == FactualVerdict.AMBIGUOUS_OR_CONFLICTING
    assert "conflicting" in finding.explanation.lower()


# ==============================================================================
# 5. CITATION SUPPORT CHECK (Cases 12 - 13)
# ==============================================================================

def test_case_12_citation_missing_date():
    """Case 12: Citation Check - Candidate passage missing asserted date"""
    claim = "The congress convened in 1815 to redraw European borders."
    quote = "The diplomatic congress convened to redraw European borders after the war."
    is_ver, reason = verify_citation_support(claim, quote)
    assert is_ver is False
    assert "1815" in reason

def test_case_13_citation_missing_named_entity():
    """Case 13: Citation Check - Candidate passage missing unique proper noun"""
    claim = "The Hubble Space Telescope confirmed cosmic acceleration."
    quote = "Space telescopes confirmed cosmic acceleration using supernovae surveys."
    is_ver, reason = verify_citation_support(claim, quote)
    assert is_ver is False
    assert "hubble" in reason.lower()


# ==============================================================================
# 6. STRICT SSRF DEFENSE (Cases 14 - 16)
# ==============================================================================

def test_case_14_ssrf_loopback_blocked():
    """Case 14: SSRF Defense - Loopback address blocked"""
    with pytest.raises(SecondOpinionException) as exc:
        validate_url_and_check_ssrf("http://127.0.0.1:8080/admin")
    assert exc.value.detail["code"] == ErrorCode.INVALID_INPUT.value
    assert "blocked private, loopback, or metadata IP" in exc.value.detail["message"]

def test_case_15_ssrf_cloud_metadata_blocked():
    """Case 15: SSRF Defense - Cloud metadata endpoint 169.254.169.254 blocked"""
    with pytest.raises(SecondOpinionException) as exc:
        validate_url_and_check_ssrf("http://169.254.169.254/computeMetadata/v1/")
    assert exc.value.detail["code"] == ErrorCode.INVALID_INPUT.value

def test_case_16_ssrf_forbidden_scheme_blocked():
    """Case 16: SSRF Defense - Disallowed file:// URI scheme blocked"""
    with pytest.raises(SecondOpinionException) as exc:
        validate_url_and_check_ssrf("file:///etc/shadow")
    assert exc.value.detail["code"] == ErrorCode.INVALID_INPUT.value


# ==============================================================================
# 7. WEB URL INGESTION (Case 17)
# ==============================================================================

@pytest.mark.anyio
async def test_case_17_user_url_ingestion():
    """Case 17: User URL Ingestion - Ingests web page and tags provenance as user_url"""
    html_page = "<html><head><title>Titan Atmosphere</title></head><body><p>Titan possesses a dense nitrogen-rich atmosphere with methane clouds.</p></body></html>"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = html_page.encode("utf-8")

    with patch("backend.app.services.url_fetcher.validate_url_and_check_ssrf"):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            res = await process_audit(
                answer="Titan has a dense nitrogen atmosphere with methane clouds.",
                urls="https://astronomy.example.com/titan"
            )
            assert len(res.sources) > 0
            assert res.sources[0].media_type == "text/html"
            assert res.findings[0].evidence[0].origin_type == "user_url"
            assert res.findings[0].evidence[0].source_url == "https://astronomy.example.com/titan"


# ==============================================================================
# 8. NO-SOURCE WEB MODE (Case 18)
# ==============================================================================

@pytest.mark.anyio
async def test_case_18_no_source_web_mode():
    """Case 18: No-Source Mode - Free web evidence retrieval via Wikipedia/arXiv"""
    mock_wiki = [
        WebSearchResult(
            title="General relativity",
            snippet="General relativity is Einstein's geometric theory of gravitation, published in 1915.",
            url="https://en.wikipedia.org/wiki/General_relativity",
            source_name="Wikipedia",
            origin_type="wikipedia"
        )
    ]
    with patch("backend.app.services.web_evidence.provider_chain.WebEvidenceChain.fetch_evidence_for_query", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_wiki

        res = await process_audit(
            answer="Albert Einstein formulated general relativity in 1915.",
            source_text=None,
            files=None,
            enable_web_search_flag=True
        )
        assert res.source_mode == "web_search"
        assert res.findings[0].evidence[0].origin_type == "wikipedia"


# ==============================================================================
# 9. COST GUARD & PRIVACY (Cases 19 - 20)
# ==============================================================================

def test_case_19_checkability_filters_banter():
    """Case 19: Checkability Filter - Conversational boilerplate is discarded"""
    filler = "I hope this helps you understand the topic better! Let me know if you need anything else."
    is_ch, reason = is_checkable_claim(filler)
    assert is_ch is False
    assert "filler" in reason.lower()

def test_case_20_cost_budget_cap_enforced():
    """Case 20: Cost Guard - Strict query limit enforced"""
    tracker = CostBudgetTracker(max_queries=3)
    assert tracker.can_query() is True
    tracker.record_query()
    tracker.record_query()
    tracker.record_query()
    assert tracker.can_query() is False
    assert tracker.is_budget_exhausted is True
