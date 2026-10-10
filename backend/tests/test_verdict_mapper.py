"""
Tests for Verdict Mapper, Deterministic Rules, and Audit Summary Aggregation.
Verifies:
1. Distinct outcomes: SUPPORTED, CONTRADICTED, NOT_ESTABLISHED, AMBIGUOUS
2. Missing evidence is NEVER marked false/contradicted
3. Transparent summary counts without ungrounded universal accuracy percentage
"""
import json
from pathlib import Path

from backend.app.schemas import Claim, FactualVerdict
from backend.app.services.document_parser import parse_plain_text
from backend.app.services.source_chunks import chunk_document
from backend.app.services.retriever import BM25Retriever
from backend.app.services.verdict_mapper import map_verdict_for_claim
from backend.app.services.summary_service import generate_audit_summary

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_verdict_mapping_on_synthetic_fixtures():
    # Load policy source
    policy_text = (FIXTURES_DIR / "sample_policy.txt").read_text(encoding="utf-8")
    parsed_source = parse_plain_text(policy_text, "sample_policy.txt")
    chunks = chunk_document(parsed_source, target_words=50, overlap_words=10)
    retriever = BM25Retriever(chunks)

    # Load mixed answer fixture
    mixed_data = json.loads((FIXTURES_DIR / "sample_mixed_answer.json").read_text(encoding="utf-8"))
    
    findings = []
    for item in mixed_data["expected_evaluations"]:
        claim_text = item["claim_text"]
        expected_verdict = item["expected_verdict"]

        claim = Claim(
            claim_id="clm_test",
            text=claim_text,
            start_char=0,
            end_char=len(claim_text),
            parent_sentence=claim_text
        )

        candidates = retriever.retrieve_candidates(claim_text, top_k=2)
        finding = map_verdict_for_claim(claim, candidates, nli_verifier=None)
        findings.append(finding)

        assert finding.verdict.value == expected_verdict, (
            f"Expected {expected_verdict} for '{claim_text}', got {finding.verdict.value}. "
            f"Explanation: {finding.explanation}"
        )

    # Verify Summary Aggregation
    summary = generate_audit_summary(findings)
    assert summary.total_claims == 3
    assert summary.supported_claims == 1
    assert summary.contradicted_claims == 1
    assert summary.not_established_claims == 1
    assert summary.ambiguous_claims == 0
    assert summary.assessment == "Contradictions Detected"
    assert "High Priority" in summary.review_recommendation

def test_missing_evidence_is_not_contradicted():
    """
    CRITICAL RULE (§2, §15.3): A claim completely missing from the sources
    must be marked NOT_ESTABLISHED_BY_SOURCE, NEVER CONTRADICTED_BY_SOURCE.
    """
    claim = Claim(
        claim_id="clm_unrelated",
        text="Mars rover discovered liquid water in crater Gale.",
        start_char=0,
        end_char=52,
        parent_sentence="Mars rover discovered liquid water in crater Gale."
    )

    finding = map_verdict_for_claim(claim, candidate_evidence=[], nli_verifier=None)
    assert finding.verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
    assert finding.verdict != FactualVerdict.CONTRADICTED_BY_SOURCE
    assert "No relevant evidence passage was found" in finding.explanation

def test_safety_flags_are_separated_from_verdict():
    """
    CRITICAL RULE (§2, §9.7): Safety concerns must not distort the factual verdict.
    """
    claim = Claim(
        claim_id="clm_med",
        text="The doctor prescribed 50mg of antibiotics to cure the symptoms.",
        start_char=0,
        end_char=65,
        parent_sentence="The doctor prescribed 50mg of antibiotics to cure the symptoms."
    )

    finding = map_verdict_for_claim(claim, candidate_evidence=[], nli_verifier=None)
    assert len(finding.safety_concerns) > 0
    assert "Health/Medical advisory" in finding.safety_concerns[0]
    # Factually, since no source was provided, it is not established, not failed/errored
    assert finding.verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
