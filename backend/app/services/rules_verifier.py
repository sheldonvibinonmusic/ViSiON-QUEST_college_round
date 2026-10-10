"""
Deterministic rules engine for date, numerical, and negation discrepancies.
Provides reliable, zero-cost, transparent rule-based verification signals.
Ensures that missing topics or section numbers are NEVER falsely treated as contradictions.
"""
import re
from typing import List, Tuple, Set, Optional

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
    "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "addition", "also"
}

def extract_numbers_and_currency(text: str) -> Set[str]:
    """
    Extract currency values, percentages, and multi-digit quantities.
    Ignores isolated section digits (like '1.', '2.').
    """
    patterns = [
        r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?',  # Currency $500
        r'\b\d+(?:\.\d+)?\s*%',              # Percentage 4.5%
        r'\b\d{2,}(?:,\d{3})*(?:\.\d+)?\b'   # Multi-digit numbers (avoids list numbers like 1, 2)
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
    words = set(re.findall(r'\b[a-z\']+\b', text.lower()))
    return len(words.intersection(NEGATION_TERMS)) > 0

class RuleCheckResult:
    def __init__(
        self,
        is_contradiction: bool = False,
        is_supported: bool = False,
        reasons: Optional[List[str]] = None,
        logic_concerns: Optional[List[str]] = None
    ):
        self.is_contradiction = is_contradiction
        self.is_supported = is_supported
        self.reasons = reasons or []
        self.logic_concerns = logic_concerns or []

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
    claim_words = set(re.findall(r'\b[a-z]{3,}\b', claim_text.lower())) - STOP_WORDS
    sentences = split_into_sentences(evidence_quote)
    if not sentences:
        return evidence_quote, 0

    best_sent = sentences[0]
    best_overlap = 0

    for s in sentences:
        s_words = set(re.findall(r'\b[a-z]{3,}\b', s.lower())) - STOP_WORDS
        overlap = len(claim_words.intersection(s_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_sent = s

    return best_sent, best_overlap

def evaluate_rules(claim_text: str, evidence_quote: str) -> RuleCheckResult:
    """
    Compare claim text against candidate evidence quote using deterministic rules.
    CRITICAL RULE (§2, §15.3):
    Only triggers contradiction if the candidate evidence sentence explicitly shares
    topic context (at least 2 substantive non-stopword tokens).
    """
    reasons: List[str] = []
    logic_concerns: List[str] = []
    is_contradiction = False
    is_supported = False

    claim_lower = claim_text.lower()
    target_sentence, overlap_count = find_best_matching_sentence(claim_text, evidence_quote)
    target_lower = target_sentence.lower()

    # Identify substantive shared keywords
    claim_words = (
        set(re.findall(r'\b[a-z]{3,}\b', claim_lower))
        - NEGATION_TERMS - AFFIRMATIVE_TERMS - STOP_WORDS
    )
    target_words = (
        set(re.findall(r'\b[a-z]{3,}\b', target_lower))
        - NEGATION_TERMS - AFFIRMATIVE_TERMS - STOP_WORDS
    )
    shared_content = claim_words.intersection(target_words)

    # If there is insufficient topical overlap, this passage does NOT substantiate or contradict the claim.
    if len(shared_content) < 2:
        return RuleCheckResult(
            is_contradiction=False,
            is_supported=False,
            reasons=["Topical overlap below threshold; evidence does not address claim subject."],
            logic_concerns=[]
        )

    # 1. Number and Currency Check (Evaluated only on topic-aligned sentence)
    claim_nums = extract_numbers_and_currency(claim_text)
    target_nums = extract_numbers_and_currency(target_sentence)

    if claim_nums and target_nums:
        common_nums = claim_nums.intersection(target_nums)
        differing_claim = claim_nums - target_nums
        differing_target = target_nums - claim_nums

        if differing_claim and differing_target and not common_nums:
            is_contradiction = True
            reasons.append(
                f"Numerical discrepancy on shared subject: claim states {', '.join(differing_claim)} while source states {', '.join(differing_target)}."
            )
        elif common_nums:
            reasons.append(f"Matching numerical values verified: {', '.join(common_nums)}.")

    # 2. Year and Date Check
    claim_dates = extract_years_and_dates(claim_text)
    target_dates = extract_years_and_dates(target_sentence)

    if claim_dates and target_dates:
        mismatched_dates = claim_dates - target_dates
        if mismatched_dates:
            is_contradiction = True
            reasons.append(
                f"Date discrepancy: claim cites {', '.join(mismatched_dates)} while source states {', '.join(target_dates)}."
            )
        else:
            reasons.append("Matching dates verified.")

    # 3. Negation & Polarity Inversion Check
    claim_neg = has_negation(claim_text)
    target_neg = has_negation(target_sentence)

    if claim_neg != target_neg:
        is_contradiction = True
        reasons.append(
            f"Polarity clash: statement polarity conflicts on topic involving {', '.join(list(shared_content)[:4])}."
        )
    elif not is_contradiction:
        is_supported = True
        reasons.append(f"Content alignment on key terms: {', '.join(list(shared_content)[:4])}.")

    # 4. Arithmetic Check
    for num_str in claim_nums:
        if num_str.endswith("%"):
            try:
                val = float(num_str[:-1])
                if val > 100:
                    logic_concerns.append(f"Percentage {num_str} exceeds 100%; verify baseline denominator.")
            except ValueError:
                pass

    return RuleCheckResult(
        is_contradiction=is_contradiction,
        is_supported=is_supported,
        reasons=reasons,
        logic_concerns=logic_concerns
    )
