"""
Modal and Negation/Opposites verification module for Second Opinion.
Detects modal inversions (must vs should, prohibited vs permissible) and
directional opposite polarity clashes (increase vs decrease, at least vs at most).
Fixes F2 (Modal Inversion) and F5 (Negation and Opposites).
"""
import re
from typing import Dict, List, Optional, Set, Tuple

# Modal classification sets
MODAL_OBLIGATION: Set[str] = {
    "must", "shall", "required", "mandatory", "mandated", "have to",
    "has to", "need to", "needs to", "obligated", "compulsory"
}

MODAL_PROHIBITION: Set[str] = {
    "prohibited", "forbidden", "banned", "not allowed", "cannot",
    "must not", "shall not", "disallowed", "ineligible"
}

MODAL_PERMISSIVE: Set[str] = {
    "may", "can", "allowed", "permitted", "permissible", "eligible",
    "optional", "authorized"
}

MODAL_RECOMMENDED: Set[str] = {
    "should", "recommended", "advised", "encouraged", "suggested",
    "ought to", "preferable"
}

# Directional opposite pairs
OPPOSITE_PAIRS: List[Tuple[Set[str], Set[str], str]] = [
    (
        {"increase", "increased", "increasing", "rise", "rose", "rising", "grow", "grew", "growth", "gain", "gained"},
        {"decrease", "decreased", "decreasing", "drop", "dropped", "dropping", "fall", "fell", "falling", "decline", "declined", "shrink", "shrank"},
        "increase vs decrease"
    ),
    (
        {"more", "greater", "higher", "above", "exceed", "exceeded", "exceeding"},
        {"less", "fewer", "lower", "below", "under"},
        "more/above vs less/below"
    ),
    (
        {"before", "prior", "preceding", "earlier"},
        {"after", "following", "subsequent", "later"},
        "before vs after"
    ),
    (
        {"at least", "minimum", "not less than", "no less than"},
        {"at most", "maximum", "not more than", "no more than", "up to"},
        "at least vs at most"
    ),
    (
        {"all", "every", "always", "entire", "complete"},
        {"some", "few", "partial", "sometimes", "none", "neither"},
        "all vs some/none"
    ),
    (
        {"allow", "allowed", "permit", "permitted", "permissible"},
        {"prohibit", "prohibited", "forbid", "forbidden", "ban", "banned", "not allowed"},
        "allowed vs prohibited"
    ),
    (
        {"domestic", "internal", "local", "national"},
        {"international", "foreign", "global", "overseas"},
        "domestic vs international"
    ),
    (
        {"public", "publicly"},
        {"private", "privately"},
        "public vs private"
    ),
    (
        {"commercial"},
        {"recreational", "hobby", "personal"},
        "commercial vs recreational"
    ),
    (
        {"adult", "adults"},
        {"minor", "minors", "child", "children", "pediatric"},
        "adult vs minor"
    ),
]


class ModalNegationResult:
    def __init__(
        self,
        has_modal_inversion: bool = False,
        has_opposite_clash: bool = False,
        has_negation_clash: bool = False,
        reasons: Optional[List[str]] = None,
        severity: str = "none"  # "contradiction", "downgrade", "none"
    ):
        self.has_modal_inversion = has_modal_inversion
        self.has_opposite_clash = has_opposite_clash
        self.has_negation_clash = has_negation_clash
        self.reasons = reasons or []
        self.severity = severity


def extract_modal_strength(text: str) -> str:
    """Classify the dominant modal strength in text: 'obligation', 'prohibition', 'permissive', 'recommended', or 'none'."""
    text_lower = text.lower()
    tokens = set(re.findall(r"\b[a-z\']+\b", text_lower))

    # Check multi-word modals first
    if "not allowed" in text_lower or "must not" in text_lower or "shall not" in text_lower:
        return "prohibition"
    if "have to" in text_lower or "has to" in text_lower or "need to" in text_lower or "needs to" in text_lower:
        return "obligation"
    if "ought to" in text_lower:
        return "recommended"

    if tokens.intersection(MODAL_PROHIBITION):
        return "prohibition"
    if tokens.intersection(MODAL_OBLIGATION):
        return "obligation"
    if tokens.intersection(MODAL_RECOMMENDED):
        return "recommended"
    if tokens.intersection(MODAL_PERMISSIVE):
        return "permissive"
    return "none"


def check_modal_and_negation(
    claim_text: str,
    evidence_text: str,
    shared_topics: Optional[Set[str]] = None
) -> ModalNegationResult:
    """
    Compare claim text against candidate evidence quote for modal inversions,
    directional opposite clashes, and negation discrepancies.
    """
    reasons: List[str] = []
    has_modal_inversion = False
    has_opposite_clash = False
    has_negation_clash = False
    severity = "none"

    claim_lower = claim_text.lower()
    evidence_lower = evidence_text.lower()

    # 1. Modal Inversion Check (F2)
    claim_modal = extract_modal_strength(claim_lower)
    evidence_modal = extract_modal_strength(evidence_lower)

    if claim_modal != "none" and evidence_modal != "none":
        # Source says should/recommended/permissive, but claim asserts must/mandated
        if evidence_modal in ("recommended", "permissive") and claim_modal == "obligation":
            has_modal_inversion = True
            reasons.append(
                f"Modal shift: source states '{evidence_modal}' (e.g. should/recommended/may) while claim asserts '{claim_modal}' (must/shall/required)"
            )
            severity = "downgrade"
        # Source says prohibited, claim says permitted
        elif evidence_modal == "prohibition" and claim_modal in ("permissive", "recommended"):
            has_modal_inversion = True
            reasons.append(
                "Modal clash: source prohibits or restricts action while claim asserts it is permitted/allowed"
            )
            severity = "contradiction"
        # Source says permitted, claim says prohibited
        elif evidence_modal in ("permissive", "recommended") and claim_modal == "prohibition":
            has_modal_inversion = True
            reasons.append(
                "Modal clash: source permits or recommends action while claim asserts it is prohibited"
            )
            severity = "contradiction"

    # 2. Directional Opposites Check (F5)
    for group_a, group_b, label in OPPOSITE_PAIRS:
        # Check phrase and token presence
        claim_has_a = any(term in claim_lower for term in group_a)
        claim_has_b = any(term in claim_lower for term in group_b)
        ev_has_a = any(term in evidence_lower for term in group_a)
        ev_has_b = any(term in evidence_lower for term in group_b)

        if (claim_has_a and ev_has_b and not ev_has_a) or (claim_has_b and ev_has_a and not ev_has_b):
            has_opposite_clash = True
            reasons.append(
                f"Directional opposite clash on '{label}': claim and source assert opposing conditions"
            )
            severity = "contradiction"

    # 3. Simple Polarity / Negation Inversion
    negation_words = {"not", "never", "no", "cannot", "without", "neither", "nor"}
    claim_has_neg = any(w in re.findall(r"\b[a-z']+\b", claim_lower) for w in negation_words)
    ev_has_neg = any(w in re.findall(r"\b[a-z']+\b", evidence_lower) for w in negation_words)

    # Check if negation words explicitly modify shared key predicates
    if claim_has_neg != ev_has_neg and not has_opposite_clash and not has_modal_inversion:
        # Check for phrase-level negations (e.g., 'not allowed' vs 'allowed')
        has_negation_clash = True
        reasons.append("Polarity clash: statement negation differs between claim and source")
        severity = "contradiction"

    return ModalNegationResult(
        has_modal_inversion=has_modal_inversion,
        has_opposite_clash=has_opposite_clash,
        has_negation_clash=has_negation_clash,
        reasons=reasons,
        severity=severity
    )
