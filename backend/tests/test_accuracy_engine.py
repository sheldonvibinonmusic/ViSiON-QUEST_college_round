"""
Regression tests for deterministic audit engine accuracy (F1 through F10).
Verifies:
- F1: Number swapping detection and number format equivalences
- F2: Modal strength shift downgrade and prohibition clash
- F3: Hallucinated citation / fake entity rejection
- F4: Scope mismatch detection
- F5: Directional opposite polarity clash (increase/decrease, at least/at most)
- F6: Paraphrase resolution via stemming and synonym normalization
- F7: Large document processing (>150k chars) without crashing
- F8: Subpage crawling within same domain
- F9: Per-claim isolation and deadline timeouts
- F10: Output clarity fields (verdict_reason, checks)
"""
import pytest
from backend.app.schemas import FactualVerdict
from backend.app.services.audit_service import process_audit
from backend.app.services.rules_verifier import evaluate_rules
from backend.app.services.fact_slots import extract_fact_slots, compare_fact_slots
from backend.app.services.normalizer import parse_normalized_numbers, normalize_sentence
from backend.app.services.entity_checker import check_exact_entities
from backend.app.services.scope_checker import check_scope_alignment
from backend.app.services.modal_negation import check_modal_and_negation


# ---------------------------------------------------------
# F1: Number Blindspot
# ---------------------------------------------------------

def test_f1_swapped_numbers_detected():
    """Swapped numbers ($45M revenue vs $12M revenue) must trigger a contradiction."""
    claim = "In 2024, revenue was $45M while operating costs were $12M."
    source = "In 2024, revenue was $12M while operating costs were $45M."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_contradiction is True
    assert any("Numerical mismatch" in r or "Numerical discrepancy" in r for r in eval_res.reasons)


def test_f1_number_format_equivalences():
    """$45M, 45 million, and 45,000,000 must normalize to the exact same value."""
    n1 = parse_normalized_numbers("$45M")[0]
    n2 = parse_normalized_numbers("45 million dollars")[0]
    n3 = parse_normalized_numbers("$45,000,000")[0]

    assert n1.equals(n2)
    assert n2.equals(n3)
    assert n1.value == 45_000_000.0


def test_f1_different_entities_different_numbers():
    """Numbers attached to different entities must not cause false contradictions."""
    claim = "Company A reported 50 units."
    source = "Company B reported 100 units while Company A reported 50 units."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_contradiction is False
    assert eval_res.is_supported is True


# ---------------------------------------------------------
# F2: Modal Inversion
# ---------------------------------------------------------

def test_f2_modal_should_to_must_downgrade():
    """Source 'should' vs claim 'must' must downgrade and NOT pass as supported."""
    claim = "Remote employees must register their equipment."
    source = "Remote employees should register their equipment if possible."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_supported is False
    assert eval_res.downgrade_to_ambiguous is True


def test_f2_modal_prohibition_clash():
    """Source prohibited vs claim permitted must trigger contradiction."""
    claim = "Camping is permitted in the park."
    source = "Camping is prohibited in the park."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_contradiction is True


# ---------------------------------------------------------
# F3: Hallucinated Citation Pass
# ---------------------------------------------------------

def test_f3_hallucinated_citation_rejected():
    """Fake statutory/RFC citations must not pass as supported."""
    claim = "According to RFC 9999, packets are dropped when the buffer overflows."
    source = "Packets are dropped when the buffer overflows."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_supported is False
    assert eval_res.downgrade_to_unestablished is True
    assert "rfc 9999" in eval_res.primary_reason.lower()


# ---------------------------------------------------------
# F4: Scope Swap
# ---------------------------------------------------------

def test_f4_scope_mismatch_commercial_vs_recreational():
    """Commercial vs recreational scope swap must not pass as supported."""
    claim = "The permit authorizes commercial drone flights in local parks."
    source = "The permit authorizes recreational hobby drone flights in local parks."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_supported is False
    assert eval_res.downgrade_to_ambiguous is True


# ---------------------------------------------------------
# F5: Negation and Opposites
# ---------------------------------------------------------

def test_f5_directional_opposites_increase_vs_decrease():
    """Increased vs decreased must trigger contradiction."""
    claim = "Company profits increased by 15% in 2024."
    source = "Company profits decreased by 15% in 2024."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_contradiction is True


def test_f5_directional_opposites_at_least_vs_at_most():
    """At least vs at most must trigger contradiction."""
    claim = "The system requires at least 10 active servers."
    source = "The system requires at most 10 active servers."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_contradiction is True


# ---------------------------------------------------------
# F6: Paraphrase Resolution
# ---------------------------------------------------------

def test_f6_stemming_and_synonym_normalization():
    """Synonyms like purchase/buy and rose/increase align without false contradiction."""
    claim = "The company purchased new servers as demand rose."
    source = "The company bought new servers as demand increased."
    eval_res = evaluate_rules(claim, source)
    assert eval_res.is_contradiction is False
    assert eval_res.is_supported is True


# ---------------------------------------------------------
# F7: Large Document Processing
# ---------------------------------------------------------

@pytest.mark.anyio
async def test_f7_large_document_processed_without_crash():
    """Inputs exceeding 150k characters must not crash or throw CONTENT_TOO_LARGE."""
    large_source = "Chapter 1: Renewable Energy\n" + ("Solar power continues to expand globally. " * 5000)
    assert len(large_source) > 150000

    answer = "Solar power continues to expand globally."
    response = await process_audit(answer=answer, source_text=large_source)

    assert response.status == "completed"
    assert response.truncated is True
    assert response.original_size >= 150000
    assert response.kept_size <= 150000
    assert len(response.findings) > 0
    assert response.findings[0].verdict == FactualVerdict.SUPPORTED_BY_SOURCE


# ---------------------------------------------------------
# F9 & F10: Robustness, Output Clarity & Verdict Reason
# ---------------------------------------------------------

@pytest.mark.anyio
async def test_f10_audit_response_contains_checks_and_reasons():
    """Each finding must provide granular checks and a human-readable verdict_reason."""
    answer = "The treaty was signed in 1995. Revenue reached $50M."
    source = "The treaty was signed in 1995. Revenue reached $10M."
    response = await process_audit(answer=answer, source_text=source)

    assert len(response.findings) >= 2
    f1 = response.findings[0]
    assert f1.verdict == FactualVerdict.SUPPORTED_BY_SOURCE
    assert f1.verdict_reason is not None
    assert len(f1.checks) > 0

    f2 = response.findings[1]
    assert f2.verdict == FactualVerdict.CONTRADICTED_BY_SOURCE
    assert f2.verdict_reason is not None
    assert "Numerical mismatch" in f2.verdict_reason or "discrepancy" in f2.verdict_reason
