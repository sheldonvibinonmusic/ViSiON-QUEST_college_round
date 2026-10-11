"""
Scope verification module for Second Opinion.
Detects domain and audience scope mismatches (commercial vs recreational,
adult vs minor, public vs private, federal vs state) across claims, evidence,
and governing section headings. Fixes F4 (Scope Swap).
"""
import re
from typing import Dict, List, Optional, Set, Tuple

SCOPE_CATEGORIES: List[Tuple[str, Set[str], Set[str]]] = [
    (
        "commercial vs recreational",
        {"commercial", "business", "enterprise", "for-profit", "professional"},
        {"recreational", "hobby", "personal", "leisure", "amateur", "non-commercial"}
    ),
    (
        "adult vs minor",
        {"adult", "adults", "grown-up", "mature", "18 and over", "18+"},
        {"minor", "minors", "child", "children", "pediatric", "under 18", "infant", "juvenile"}
    ),
    (
        "public vs private",
        {"public", "publicly", "government", "state-owned", "open-access"},
        {"private", "privately", "proprietary", "confidential", "restricted-access"}
    ),
    (
        "federal vs state/local",
        {"federal", "national", "nationwide"},
        {"state", "provincial", "local", "municipal", "county", "city"}
    ),
    (
        "domestic vs international",
        {"domestic", "internal", "national"},
        {"international", "foreign", "global", "overseas", "cross-border"}
    ),
    (
        "full-time vs part-time",
        {"full-time", "full time", "regular"},
        {"part-time", "part time", "temporary", "contractor", "intern"}
    ),
    (
        "inpatient vs outpatient",
        {"inpatient", "hospitalized", "admitted"},
        {"outpatient", "ambulatory", "clinic"}
    ),
]


class ScopeCheckResult:
    def __init__(
        self,
        has_scope_conflict: bool = False,
        claim_scope: str = "",
        evidence_scope: str = "",
        category_label: str = "",
        reason: str = ""
    ):
        self.has_scope_conflict = has_scope_conflict
        self.claim_scope = claim_scope
        self.evidence_scope = evidence_scope
        self.category_label = category_label
        self.reason = reason


def check_scope_alignment(
    claim_text: str,
    evidence_text: str,
    section_heading: Optional[str] = None
) -> ScopeCheckResult:
    """
    Check if the claim's asserted scope matches or conflicts with the evidence quote
    and its governing section heading.
    """
    claim_lower = claim_text.lower()
    evidence_context = (evidence_text + " " + (section_heading or "")).lower()

    for label, group_a, group_b in SCOPE_CATEGORIES:
        claim_has_a = any(term in claim_lower for term in group_a)
        claim_has_b = any(term in claim_lower for term in group_b)

        ev_has_a = any(term in evidence_context for term in group_a)
        ev_has_b = any(term in evidence_context for term in group_b)

        # Claim explicitly asserts scope A, but evidence/heading explicitly specifies scope B
        if claim_has_a and ev_has_b and not ev_has_a:
            matched_claim = [t for t in group_a if t in claim_lower][0]
            matched_ev = [t for t in group_b if t in evidence_context][0]
            return ScopeCheckResult(
                has_scope_conflict=True,
                claim_scope=matched_claim,
                evidence_scope=matched_ev,
                category_label=label,
                reason=f"Scope mismatch ({label}): claim specifies '{matched_claim}' while source governs '{matched_ev}'"
            )

        # Claim explicitly asserts scope B, but evidence/heading explicitly specifies scope A
        if claim_has_b and ev_has_a and not ev_has_b:
            matched_claim = [t for t in group_b if t in claim_lower][0]
            matched_ev = [t for t in group_a if t in evidence_context][0]
            return ScopeCheckResult(
                has_scope_conflict=True,
                claim_scope=matched_claim,
                evidence_scope=matched_ev,
                category_label=label,
                reason=f"Scope mismatch ({label}): claim specifies '{matched_claim}' while source governs '{matched_ev}'"
            )

    return ScopeCheckResult(has_scope_conflict=False)
