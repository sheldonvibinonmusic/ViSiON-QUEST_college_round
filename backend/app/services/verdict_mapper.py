"""
Verdict Mapping Service.
Combines retrieval rank, deterministic rule signals, and NLI inference into
the 4 canonical factual verdicts:
1. SUPPORTED_BY_SOURCE
2. CONTRADICTED_BY_SOURCE
3. NOT_ESTABLISHED_BY_SOURCE
4. AMBIGUOUS_OR_CONFLICTING
"""
from typing import List, Optional, Dict, Any

from backend.app.schemas import (
    Claim,
    EvidenceReference,
    ClaimFinding,
    FactualVerdict,
)
from backend.app.services.rules_verifier import evaluate_rules, RuleCheckResult
from backend.app.services.safety_flags import check_safety_concerns
from backend.app.services.nli_verifier import NLIVerifier
from backend.app.errors import WarningCode

def map_verdict_for_claim(
    claim: Claim,
    candidate_evidence: List[EvidenceReference],
    nli_verifier: Optional[NLIVerifier] = None
) -> ClaimFinding:
    """
    Map candidate evidence and signals to an authoritative ClaimFinding.
    """
    safety_concerns = check_safety_concerns(claim.text)
    logic_concerns: List[str] = []
    warnings: List[str] = []
    model_details: Optional[Dict[str, Any]] = None

    # Case 1: No candidate evidence was retrieved by BM25
    if not candidate_evidence:
        return ClaimFinding(
            claim_id=claim.claim_id,
            claim_text=claim.text,
            start_char=claim.start_char,
            end_char=claim.end_char,
            verdict=FactualVerdict.NOT_ESTABLISHED_BY_SOURCE,
            explanation="No relevant evidence passage was found in the provided source documents to assess this claim.",
            evidence=[],
            logic_concerns=[],
            safety_concerns=safety_concerns,
            review_priority="medium",
            evidence_strength=0.0,
            model_details=None,
            warnings=[]
        )

    # Evaluate candidates with rules and optional NLI
    top_candidate = candidate_evidence[0]
    rule_eval: RuleCheckResult = evaluate_rules(claim.text, top_candidate.quote)
    logic_concerns.extend(rule_eval.logic_concerns)

    # Run NLI if model is loaded/available
    nli_scores = None
    if nli_verifier:
        nli_scores = nli_verifier.predict_pair(premise=top_candidate.quote, hypothesis=claim.text)
        if nli_scores:
            model_details = {
                "nli_scores": nli_scores,
                "verifier_mode": "rules_and_model"
            }
        else:
            warnings.append(WarningCode.MODEL_FALLBACK_RULES_ONLY.value)
    else:
        warnings.append(WarningCode.MODEL_FALLBACK_RULES_ONLY.value)

    # Check for conflicting evidence across multiple candidate passages
    second_eval = evaluate_rules(claim.text, candidate_evidence[1].quote) if len(candidate_evidence) > 1 else None

    # Priority A: Multiple candidates provide conflicting evidence
    if second_eval and (
        (rule_eval.is_supported and second_eval.is_contradiction) or
        (rule_eval.is_contradiction and second_eval.is_supported)
    ):
        verdict = FactualVerdict.AMBIGUOUS_OR_CONFLICTING
        explanation = "Candidate passages in source documents provide conflicting or ambiguous evidence."
        review_priority = "medium"
        evidence_strength = 0.5

    # Priority B: Contradiction via rules or high NLI contradiction
    elif rule_eval.is_contradiction:
        verdict = FactualVerdict.CONTRADICTED_BY_SOURCE
        explanation = f"Source evidence contradicts claim: {' '.join(rule_eval.reasons)}"
        review_priority = "high"
        evidence_strength = 0.9

    elif nli_scores and nli_scores.get("contradiction", 0.0) >= 0.7:
        verdict = FactualVerdict.CONTRADICTED_BY_SOURCE
        explanation = f"NLI verifier identified strong contradiction with source passage: '{top_candidate.quote[:100]}...'."
        review_priority = "high"
        evidence_strength = nli_scores["contradiction"]

    # Priority C: Support via rules or high NLI entailment
    elif rule_eval.is_supported or (nli_scores and nli_scores.get("entailment", 0.0) >= 0.65):
        verdict = FactualVerdict.SUPPORTED_BY_SOURCE
        reasons_text = " ".join(rule_eval.reasons) if rule_eval.reasons else "Direct alignment with source passage."
        explanation = f"Source evidence supports claim: {reasons_text}"
        review_priority = "low"
        evidence_strength = nli_scores.get("entailment", 0.85) if nli_scores else 0.85

    else:
        # Default fallback: Insufficient evidence to substantiate or disprove
        verdict = FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
        explanation = "Candidate source passages mention related topics but do not sufficiently establish or contradict the claim."
        review_priority = "medium"
        evidence_strength = 0.3

    # Update candidate relation
    if verdict == FactualVerdict.SUPPORTED_BY_SOURCE:
        top_candidate.relation = "supports"
    elif verdict == FactualVerdict.CONTRADICTED_BY_SOURCE:
        top_candidate.relation = "contradicts"
    else:
        top_candidate.relation = "insufficient"

    return ClaimFinding(
        claim_id=claim.claim_id,
        claim_text=claim.text,
        start_char=claim.start_char,
        end_char=claim.end_char,
        verdict=verdict,
        explanation=explanation,
        evidence=candidate_evidence,
        logic_concerns=logic_concerns,
        safety_concerns=safety_concerns,
        review_priority=review_priority,
        evidence_strength=evidence_strength,
        model_details=model_details,
        warnings=warnings
    )
