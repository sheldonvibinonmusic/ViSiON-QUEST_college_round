"""
Verdict Mapping Service.
Combines retrieval rank, deterministic rule signals, and NLI inference into
the 4 canonical factual verdicts:
1. SUPPORTED_BY_SOURCE
2. CONTRADICTED_BY_SOURCE
3. NOT_ESTABLISHED_BY_SOURCE
4. AMBIGUOUS_OR_CONFLICTING
"""
import re
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
from backend.app.services.citation_checker import verify_citation_support
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
            warnings=[],
            checks=[{"check": "retrieval", "passed": False, "detail": "No candidate evidence passages found"}],
            verdict_reason="No relevant source passage found.",
            independent_sources_agreeing=0
        )

    # Run Citation Support Check on all candidates
    for cand in candidate_evidence:
        is_verified, reason = verify_citation_support(claim.text, cand.quote)
        cand.citation_verified = is_verified

    # Evaluate candidates with rules and optional NLI
    top_candidate = candidate_evidence[0]
    rule_eval: RuleCheckResult = evaluate_rules(
        claim.text,
        top_candidate.quote,
        section_heading=top_candidate.section
    )
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
    second_eval = evaluate_rules(
        claim.text,
        candidate_evidence[1].quote,
        section_heading=candidate_evidence[1].section
    ) if len(candidate_evidence) > 1 else None

    # Priority A: Multiple candidates provide conflicting evidence on shared substantive subject
    genuine_conflict = False
    if second_eval and (
        (rule_eval.is_supported and second_eval.is_contradiction) or
        (rule_eval.is_contradiction and second_eval.is_supported)
    ):
        claim_distinctive = {
            w.lower() for w in re.findall(r"\b[a-z]{4,}\b", claim.text.lower())
            if w.lower() not in {"employees", "company", "policy", "request", "person", "rules", "system", "working", "remotely"}
        }
        cand0_words = set(re.findall(r"\b[a-z]{4,}\b", top_candidate.quote.lower()))
        cand1_words = set(re.findall(r"\b[a-z]{4,}\b", candidate_evidence[1].quote.lower()))
        shared_0 = claim_distinctive.intersection(cand0_words)
        shared_1 = claim_distinctive.intersection(cand1_words)

        # Candidate 0 specifically addresses subject nouns (e.g. 'laptops') that candidate 1 lacks
        subject_nouns_0 = {w for w in shared_0 if w not in {"reimbursement", "purchase", "eligible", "allowed", "receive"}}
        subject_nouns_1 = {w for w in shared_1 if w not in {"reimbursement", "purchase", "eligible", "allowed", "receive"}}

        if subject_nouns_0 and not subject_nouns_1:
            genuine_conflict = False
        elif shared_0 and not shared_1:
            genuine_conflict = False
        else:
            genuine_conflict = True

    if genuine_conflict:
        verdict = FactualVerdict.AMBIGUOUS_OR_CONFLICTING
        explanation = "Candidate passages in source documents provide conflicting or ambiguous evidence."
        verdict_reason = "Conflicting evidence across candidate passages in source."
        review_priority = "medium"
        evidence_strength = 0.5

    # Priority B: Contradiction via rules or high NLI contradiction
    elif rule_eval.is_contradiction:
        verdict = FactualVerdict.CONTRADICTED_BY_SOURCE
        explanation = f"Source evidence contradicts claim: {' '.join(rule_eval.reasons)}"
        verdict_reason = rule_eval.primary_reason or "Contradicted by source passage."
        review_priority = "high"
        evidence_strength = 0.9

    elif rule_eval.downgrade_to_ambiguous:
        verdict = FactualVerdict.AMBIGUOUS_OR_CONFLICTING
        explanation = f"Source evidence contains scope or modal ambiguity: {' '.join(rule_eval.reasons)}"
        verdict_reason = rule_eval.primary_reason or "Scope or modal divergence leaves claim ambiguous."
        review_priority = "medium"
        evidence_strength = 0.5

    elif rule_eval.downgrade_to_unestablished:
        verdict = FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
        explanation = "Candidate source passages mention related topics but do not sufficiently establish or contradict the claim."
        verdict_reason = rule_eval.primary_reason or "Asserted entities, citations, or details not established."
        review_priority = "medium"
        evidence_strength = 0.3


    elif nli_scores and nli_scores.get("contradiction", 0.0) >= 0.7:
        verdict = FactualVerdict.CONTRADICTED_BY_SOURCE
        explanation = f"NLI verifier identified strong contradiction with source passage: '{top_candidate.quote[:100]}...'."
        verdict_reason = "NLI model identified semantic contradiction."
        review_priority = "high"
        evidence_strength = nli_scores["contradiction"]

    # Priority C: Support via rules or high NLI entailment, confirmed by citation check
    elif (rule_eval.is_supported or (nli_scores and nli_scores.get("entailment", 0.0) >= 0.65)) and top_candidate.citation_verified:
        verdict = FactualVerdict.SUPPORTED_BY_SOURCE
        reasons_text = " ".join(rule_eval.reasons) if rule_eval.reasons else "Direct alignment with source passage."
        explanation = f"Source evidence supports claim: {reasons_text}"
        verdict_reason = rule_eval.primary_reason or "Source evidence directly confirms asserted facts."
        review_priority = "low"
        evidence_strength = nli_scores.get("entailment", 0.85) if nli_scores else 0.85

    else:
        # Default fallback: Insufficient evidence or unverified citation
        verdict = FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
        if (rule_eval.is_supported or (nli_scores and nli_scores.get("entailment", 0.0) >= 0.65)) and not top_candidate.citation_verified:
            explanation = "Candidate source passage mentions related terms but does not substantively verify asserted numbers, dates, or named entities."
            verdict_reason = "Asserted numbers, dates, or citations unverified."
        else:
            explanation = "Candidate source passages mention related topics but do not sufficiently establish or contradict the claim."
            verdict_reason = "Evidence mentions related topic but is insufficient to verify."
        review_priority = "medium"
        evidence_strength = 0.3

    # Update candidate relation
    if verdict == FactualVerdict.SUPPORTED_BY_SOURCE:
        top_candidate.relation = "supports"
    elif verdict == FactualVerdict.CONTRADICTED_BY_SOURCE:
        top_candidate.relation = "contradicts"
    else:
        top_candidate.relation = "insufficient"

    # Compute independent corroborating sources
    if verdict == FactualVerdict.SUPPORTED_BY_SOURCE:
        agreeing_sources = {c.source_id for c in candidate_evidence if c.citation_verified}
        independent_sources_count = max(1, len(agreeing_sources))
    elif verdict == FactualVerdict.CONTRADICTED_BY_SOURCE:
        independent_sources_count = max(1, len({c.source_id for c in candidate_evidence}))
    else:
        independent_sources_count = 0

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
        warnings=warnings,
        independent_sources_agreeing=independent_sources_count,
        checks=rule_eval.checks,
        verdict_reason=verdict_reason
    )
