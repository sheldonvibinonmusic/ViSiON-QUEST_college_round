"""
Citation Support Checker Service.
Verifies whether a candidate evidence passage actually supports the claim's core
entities, numbers, dates, and predicates, preventing hallucinated or tangential citations.
"""
import re
from typing import Tuple, List, Set

from backend.app.services.rules_verifier import (
    extract_numbers_and_currency,
    extract_years_and_dates,
    STOP_WORDS,
)

COMMON_SENTENCE_STARTERS = {"The", "This", "That", "These", "Those", "There", "Here", "It", "In", "On", "At", "For", "With"}

GENERIC_ENTITY_WORDS: Set[str] = {
    "space", "telescope", "university", "institute", "hospital", "organization",
    "center", "centre", "company", "system", "theory", "model", "equation",
    "law", "paper", "project", "mission", "treaty", "republic", "kingdom",
    "state", "states", "union", "department", "agency"
}

def extract_named_entities(text: str) -> Set[str]:
    """
    Extract capitalized proper noun sequences (e.g. 'Albert Einstein', 'James Webb', 'Mars').
    Filters out common sentence-initial demonstratives/prepositions.
    """
    matches = re.findall(r'\b[A-Z][a-zA-Z0-9_-]+(?:\s+[A-Z][a-zA-Z0-9_-]+)*\b', text)
    entities = set()
    for m in matches:
        words = m.split()
        if len(words) == 1 and words[0] in COMMON_SENTENCE_STARTERS:
            continue
        entities.add(m.lower())
    return entities

def verify_citation_support(claim_text: str, quote_text: str) -> Tuple[bool, str]:
    """
    Determine if the evidence quote substantively supports the claim's key facts.
    Returns (is_verified: bool, reason: str).
    """
    claim_lower = claim_text.lower()
    quote_lower = quote_text.lower()

    # 1. Check numbers and currencies
    claim_nums = extract_numbers_and_currency(claim_text)
    quote_nums = extract_numbers_and_currency(quote_text)
    if claim_nums:
        matched_nums = claim_nums.intersection(quote_nums)
        if not matched_nums:
            return False, f"Quote does not confirm asserted numbers ({', '.join(claim_nums)})."

    # 2. Check years and dates
    claim_dates = extract_years_and_dates(claim_text)
    quote_dates = extract_years_and_dates(quote_text)
    if claim_dates:
        matched_dates = claim_dates.intersection(quote_dates)
        if not matched_dates:
            return False, f"Quote does not confirm asserted dates/years ({', '.join(claim_dates)})."

    # 3. Check named entities
    claim_entities = extract_named_entities(claim_text)
    if claim_entities:
        matched_entities = []
        for ent in claim_entities:
            ent_words = [w for w in ent.split() if w not in STOP_WORDS and len(w) >= 3]
            identifying_words = [w for w in ent_words if w not in GENERIC_ENTITY_WORDS]
            check_words = identifying_words if identifying_words else ent_words
            if ent in quote_lower or (check_words and any(w in quote_lower for w in check_words)):
                matched_entities.append(ent)
        if not matched_entities and len(claim_entities) > 0:
            return False, f"Quote lacks key entities ({', '.join(list(claim_entities)[:3])})."

    # 4. Check salient content words
    claim_words = set(re.findall(r'\b[a-z]{3,}\b', claim_lower)) - STOP_WORDS
    if not claim_words:
        # Fallback for very brief claims
        return True, "Minimal claim text matched candidate passage."

    quote_words = set(re.findall(r'\b[a-z]{3,}\b', quote_lower))
    matched_words = claim_words.intersection(quote_words)
    overlap_ratio = len(matched_words) / len(claim_words)

    if overlap_ratio < 0.35:
        return False, f"Low substantive overlap ({overlap_ratio:.0%}); quote lacks core predicates."

    return True, f"Substantive overlap ({overlap_ratio:.0%}) confirms key entities and predicates."
