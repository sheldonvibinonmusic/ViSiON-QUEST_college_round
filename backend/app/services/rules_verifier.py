"""
Deterministic rules engine for date, numerical, entity, modal, and negation discrepancies.
Provides reliable, zero-cost, transparent rule-based verification signals.
Ensures that missing topics or section numbers are NEVER falsely treated as contradictions.
"""
import re
from typing import List, Tuple, Set, Optional, Dict, Any

from backend.app.services.normalizer import (
    clean_unicode_and_whitespace,
    normalize_token,
    parse_normalized_numbers,
    NormalizedNumber,
)
from backend.app.services.fact_slots import (
    extract_fact_slots,
    compare_fact_slots,
    FactSlot,
)
from backend.app.services.modal_negation import (
    check_modal_and_negation,
    ModalNegationResult,
)
from backend.app.services.entity_checker import (
    check_exact_entities,
    extract_claim_entities,
    EntityCheckResult,
)
from backend.app.services.scope_checker import (
    check_scope_alignment,
    ScopeCheckResult,
)

NEGATION_TERMS = {
    "not", "never", "no", "cannot", "can't", "won't", "neither", "nor",
    "rejected", "reject", "prohibited", "denied", "ineligible", "without"
}

AFFIRMATIVE_TERMS = {
    "can", "eligible", "allowed", "permitted", "authorized", "provides",
    "receive", "accepted", "covered", "reimbursed"
}

STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "for", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above",
    "below", "to", "from", "up", "down", "out", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "addition", "also", "and", "or", "is", "was",
    "are", "were", "been", "be", "has", "had", "have", "that", "this",
    "which", "its", "their", "our", "it", "they", "we"
}


class RuleCheckResult:
    def __init__(
        self,
        is_contradiction: bool = False,
        is_supported: bool = False,
        downgrade_to_ambiguous: bool = False,
        downgrade_to_unestablished: bool = False,
        reasons: Optional[List[str]] = None,
        logic_concerns: Optional[List[str]] = None,
        checks: Optional[List[Dict[str, Any]]] = None,
        primary_reason: Optional[str] = None,
    ):
        self.is_contradiction = is_contradiction
        self.is_supported = is_supported
        self.downgrade_to_ambiguous = downgrade_to_ambiguous
        self.downgrade_to_unestablished = downgrade_to_unestablished
        self.reasons = reasons or []
        self.logic_concerns = logic_concerns or []
        self.checks = checks or []
        self.primary_reason = primary_reason


def extract_numbers_and_currency(text: str) -> Set[str]:
    """
    Extract currency values, percentages, and multi-digit quantities.
    Ignores isolated section digits (like '1.', '2.').
    """
    patterns = [
        r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?',  # Currency $500
        r'\b\d+(?:\.\d+)?\s*%',              # Percentage 4.5%
        r'\b\d{2,}(?:,\d{3})*(?:\.\d+)?\b'   # Multi-digit numbers
    ]
    found = set()
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            found.add(match.group(0).replace(" ", "").lower())
    return found


def extract_years_and_dates(text: str) -> Set[str]:
    """
    Extract 4-digit years (e.g. 2025, 2026) and month-day combinations.
    """
    months = r'(?:january|february|march|april|may|june|july|august|september|october|november|december)'
    pat = rf'\b(?:{months}\s+\d{{1,2}}(?:,\s*\d{{4}})?|\d{{4}})\b'
    return set(m.group(0).lower() for m in re.finditer(pat, text, re.IGNORECASE))


def has_negation(text: str) -> bool:
    """Check if text contains explicit negation words."""
    words = set(re.findall(r"\b[a-z']+\b", text.lower()))
    return len(words.intersection(NEGATION_TERMS)) > 0


def split_into_sentences(text: str) -> List[str]:
    """Split text into rough sentences for fine-grained alignment."""
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def find_best_matching_sentence(claim_text: str, evidence_quote: str) -> Tuple[str, int]:
    """
    Find the individual sentence within a multi-sentence evidence chunk
    that shares the highest word overlap with the claim.
    Returns (best_sentence, overlap_count).
    """
    claim_words = {
        normalize_token(w)
        for w in re.findall(r"\b[a-z]{3,}\b", claim_text.lower())
    } - STOP_WORDS
    sentences = split_into_sentences(evidence_quote)
    if not sentences:
        return evidence_quote, 0

    best_sent = sentences[0]
    best_overlap = 0

    for s in sentences:
        s_words = {
            normalize_token(w)
            for w in re.findall(r"\b[a-z]{3,}\b", s.lower())
        } - STOP_WORDS
        overlap = len(claim_words.intersection(s_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_sent = s

    return best_sent, best_overlap


def evaluate_rules(
    claim_text: str,
    evidence_quote: str,
    section_heading: Optional[str] = None
) -> RuleCheckResult:
    """
    Compare claim text against candidate evidence quote using deterministic rules.
    Synthesizes signals from fact_slots, modal_negation, entity_checker, and scope_checker.
    """
    reasons: List[str] = []
    logic_concerns: List[str] = []
    checks: List[Dict[str, Any]] = []
    is_contradiction = False
    is_supported = False
    downgrade_to_ambiguous = False
    downgrade_to_unestablished = False

    claim_norm = clean_unicode_and_whitespace(claim_text)
    quote_norm = clean_unicode_and_whitespace(evidence_quote)

    target_sentence, overlap_count = find_best_matching_sentence(claim_norm, quote_norm)

    # Substantive shared keywords with normalization
    claim_tokens = {
        normalize_token(w)
        for w in re.findall(r"\b[a-z]{3,}\b", claim_norm.lower())
    } - NEGATION_TERMS - AFFIRMATIVE_TERMS - STOP_WORDS

    target_tokens = {
        normalize_token(w)
        for w in re.findall(r"\b[a-z]{3,}\b", target_sentence.lower())
    } - NEGATION_TERMS - AFFIRMATIVE_TERMS - STOP_WORDS

    shared_content = claim_tokens.intersection(target_tokens)

    # Check 1: Topical Overlap Threshold (§2, §15.3)
    if len(shared_content) < 2:
        checks.append({
            "check": "topical_overlap",
            "passed": False,
            "detail": "Shared topic keywords below threshold (< 2 substantive tokens)."
        })
        return RuleCheckResult(
            is_contradiction=False,
            is_supported=False,
            downgrade_to_unestablished=True,
            reasons=["Topical overlap below threshold; evidence does not address claim subject."],
            logic_concerns=[],
            checks=checks,
            primary_reason="Topical overlap below threshold; evidence does not address claim subject."
        )

    checks.append({
        "check": "topical_overlap",
        "passed": True,
        "detail": f"Substantive topical alignment on terms: {', '.join(list(shared_content)[:4])}."
    })

    # Check 2: Exact Entity and Citation Verification (F3)
    entity_res: EntityCheckResult = check_exact_entities(claim_norm, quote_norm)
    if not entity_res.all_entities_present:
        downgrade_to_unestablished = True
        reasons.append(entity_res.reason)
        checks.append({
            "check": "exact_entities",
            "passed": False,
            "detail": entity_res.reason
        })
    elif entity_res.verified_entities:
        checks.append({
            "check": "exact_entities",
            "passed": True,
            "detail": entity_res.reason
        })

    # Check 3: Scope Alignment (F4)
    scope_res: ScopeCheckResult = check_scope_alignment(claim_norm, quote_norm, section_heading)
    if scope_res.has_scope_conflict:
        downgrade_to_ambiguous = True
        reasons.append(scope_res.reason)
        checks.append({
            "check": "scope_alignment",
            "passed": False,
            "detail": scope_res.reason
        })
    else:
        checks.append({
            "check": "scope_alignment",
            "passed": True,
            "detail": "Scope categories align."
        })

    # Check 4: Modal Inversion and Directional Opposites (F2, F5)
    modal_res: ModalNegationResult = check_modal_and_negation(claim_norm, target_sentence)
    if modal_res.has_opposite_clash:
        is_contradiction = True
        reasons.extend(modal_res.reasons)
        checks.append({
            "check": "directional_opposites",
            "passed": False,
            "detail": "; ".join(modal_res.reasons)
        })
    elif modal_res.has_modal_inversion:
        if modal_res.severity == "contradiction":
            is_contradiction = True
        else:
            downgrade_to_ambiguous = True
        reasons.extend(modal_res.reasons)
        checks.append({
            "check": "modal_strength",
            "passed": False,
            "detail": "; ".join(modal_res.reasons)
        })
    elif modal_res.has_negation_clash:
        is_contradiction = True
        reasons.extend(modal_res.reasons)
        checks.append({
            "check": "negation_polarity",
            "passed": False,
            "detail": "; ".join(modal_res.reasons)
        })
    else:
        checks.append({
            "check": "modal_and_polarity",
            "passed": True,
            "detail": "Modalities and polarities align."
        })

    # Check 5: Fact-Slot Numerical Attribute Binding (F1)
    claim_slots = extract_fact_slots(claim_norm)
    target_slots = extract_fact_slots(quote_norm)

    if claim_slots and target_slots:
        slot_res = compare_fact_slots(claim_slots, target_slots)
        if slot_res.has_slot_clash:
            is_contradiction = True
            reasons.extend(slot_res.reasons)
            checks.append({
                "check": "fact_slots",
                "passed": False,
                "detail": "; ".join(slot_res.reasons)
            })
        elif slot_res.has_slot_match:
            reasons.extend(slot_res.reasons)
            checks.append({
                "check": "fact_slots",
                "passed": True,
                "detail": "; ".join(slot_res.reasons)
            })
    else:
        # Fallback number check when attribute slots are not explicitly bound
        claim_nums = extract_numbers_and_currency(claim_norm)
        target_nums = extract_numbers_and_currency(target_sentence)
        if claim_nums and target_nums:
            common_nums = claim_nums.intersection(target_nums)
            differing_claim = claim_nums - target_nums
            differing_target = target_nums - claim_nums
            if differing_claim and differing_target and not common_nums:
                is_contradiction = True
                msg = f"Numerical discrepancy on shared subject: claim states {', '.join(differing_claim)} while source states {', '.join(differing_target)}."
                reasons.append(msg)
                checks.append({
                    "check": "numbers_currency",
                    "passed": False,
                    "detail": msg
                })
            elif common_nums:
                checks.append({
                    "check": "numbers_currency",
                    "passed": True,
                    "detail": f"Matching numerical values verified: {', '.join(common_nums)}."
                })

    # Check 6: Dates and Years
    claim_dates = extract_years_and_dates(claim_norm)
    target_dates = extract_years_and_dates(target_sentence)
    if claim_dates and target_dates:
        mismatched_dates = claim_dates - target_dates
        if mismatched_dates:
            is_contradiction = True
            msg = f"Date discrepancy: claim cites {', '.join(mismatched_dates)} while source states {', '.join(target_dates)}."
            reasons.append(msg)
            checks.append({
                "check": "dates_years",
                "passed": False,
                "detail": msg
            })
        else:
            checks.append({
                "check": "dates_years",
                "passed": True,
                "detail": "Matching dates verified."
            })

    # Check 7: Arithmetic & Logical Sanity
    for num_obj in parse_normalized_numbers(claim_norm):
        if num_obj.unit == "%" and num_obj.value > 100:
            logic_concerns.append(f"Percentage {num_obj.raw_text} exceeds 100%; verify baseline denominator.")

    # Support Decision
    if not is_contradiction and not downgrade_to_ambiguous and not downgrade_to_unestablished:
        is_supported = True
        reasons.append(f"Content alignment on key terms: {', '.join(list(shared_content)[:4])}.")

    # Primary Reason for output clarity (F10)
    primary_reason: str = ""
    if is_contradiction:
        primary_reason = reasons[0] if reasons else "Source evidence directly contradicts claim."
    elif downgrade_to_ambiguous:
        primary_reason = reasons[0] if reasons else "Scope or modal nuances present ambiguous or conflicting interpretations."
    elif downgrade_to_unestablished:
        primary_reason = entity_res.reason if (not entity_res.all_entities_present) else "Claim asserts specific entities or details not found in source passage."
    elif is_supported:
        primary_reason = reasons[0] if reasons else "Source evidence directly confirms asserted facts."
    else:
        primary_reason = "Source passage mentions related topics but does not sufficiently substantiate the claim."

    return RuleCheckResult(
        is_contradiction=is_contradiction,
        is_supported=is_supported,
        downgrade_to_ambiguous=downgrade_to_ambiguous,
        downgrade_to_unestablished=downgrade_to_unestablished,
        reasons=reasons,
        logic_concerns=logic_concerns,
        checks=checks,
        primary_reason=primary_reason,
    )
