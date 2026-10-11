"""
Fact-Slot extraction and attribute-binding service for Second Opinion.
Binds numbers, dates, and metrics to their nearest attribute nouns and entities
within a tight lexical window, preventing number blindspot errors (F1).
"""
import re
from typing import Dict, List, Optional, Set, Tuple
from backend.app.services.normalizer import (
    NormalizedNumber,
    parse_normalized_numbers,
    clean_unicode_and_whitespace,
    normalize_token,
)

# Common attribute nouns that describe metrics, quantities, or values
COMMON_ATTRIBUTES: Set[str] = {
    "revenue", "revenues", "cost", "costs", "expense", "expenses",
    "profit", "profits", "margin", "income", "sales", "earnings",
    "loss", "losses", "debt", "valuation", "budget", "price", "fee",
    "salary", "compensation", "temperature", "temp", "speed", "velocity",
    "distance", "height", "depth", "width", "length", "weight", "mass",
    "boil", "boils", "boiling", "freeze", "freezes", "freezing",
    "pressure", "altitude", "density", "volume", "capacity", "area",
    "population", "rate", "percentage", "count", "number", "shares",
    "age", "year", "years", "duration", "time", "period", "frequency",
    "unit", "units", "item", "items", "product", "products", "device", "devices"
}

STOP_TOKENS: Set[str] = {
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "are", "were", "been", "be",
    "has", "had", "have", "that", "this", "which", "its", "their", "our",
    "while", "when", "where", "after", "before", "during", "reported", "stated", "said"
}



class FactSlot:
    """Represents a bound metric: (entity, attribute, value, unit, raw_text)."""
    def __init__(
        self,
        attribute: str,
        number: NormalizedNumber,
        entity: str = "",
        qualifier: str = "",
        window_text: str = "",
    ):
        self.attribute = attribute.lower()
        self.number = number
        self.entity = entity.lower()
        self.qualifier = qualifier.lower()
        self.window_text = window_text

    def __repr__(self):
        return f"FactSlot(entity='{self.entity}', attr='{self.attribute}', val={self.number.value}, unit='{self.number.unit}')"


def extract_fact_slots(text: str) -> List[FactSlot]:
    """
    Extract all numerical/metric values in text and bind each to its nearest
    attribute word and entity within a window of 6 tokens before/after.
    """
    slots: List[FactSlot] = []
    clean_text = clean_unicode_and_whitespace(text)
    numbers = parse_normalized_numbers(clean_text)

    # Tokenize sentence with character start positions
    tokens: List[Tuple[str, int, int]] = []
    for m in re.finditer(r"\b[A-Za-z0-9_-]+\b", clean_text):
        tokens.append((m.group(0), m.start(), m.end()))

    if not tokens or not numbers:
        return slots

    for num in numbers:
        # Find index of token closest to the number's start character
        num_tok_idx = 0
        min_dist = float("inf")
        for idx, (tok_str, start_pos, end_pos) in enumerate(tokens):
            dist = abs(start_pos - num.start_char)
            if dist < min_dist:
                min_dist = dist
                num_tok_idx = idx

        # Look in window of 6 tokens before and 6 tokens after
        window_start = max(0, num_tok_idx - 6)
        window_end = min(len(tokens), num_tok_idx + 7)
        window_tokens = tokens[window_start:window_end]

        bound_attr = ""
        bound_entity = ""
        qualifier = ""

        # Check for qualifiers near number (e.g. 'at least', 'at most', 'approximately', 'over', 'under')
        qualifier_words = []
        for idx in range(max(0, num_tok_idx - 3), min(len(tokens), num_tok_idx + 1)):
            w = tokens[idx][0].lower()
            if w in ("at", "least", "most", "approx", "approximately", "over", "under", "about", "nearly"):
                qualifier_words.append(w)
        if qualifier_words:
            qualifier = " ".join(qualifier_words)

        # Identify nearest attribute noun
        # Prefer tokens BEFORE the number, then after
        best_attr_dist = float("inf")
        for idx, (tok, s_pos, _) in enumerate(window_tokens):
            w_norm = normalize_token(tok)
            w_lower = tok.lower()
            if w_lower in COMMON_ATTRIBUTES or w_norm in COMMON_ATTRIBUTES:
                dist = abs((window_start + idx) - num_tok_idx)
                if dist < best_attr_dist:
                    best_attr_dist = dist
                    bound_attr = w_norm

        # Check token immediately following the number (e.g. '50 units')
        if not bound_attr and num_tok_idx + 1 < len(tokens):
            next_w = tokens[num_tok_idx + 1][0]
            next_norm = normalize_token(next_w)
            if next_norm in COMMON_ATTRIBUTES or next_w.lower() in COMMON_ATTRIBUTES:
                bound_attr = next_norm
            elif next_w.lower() not in STOP_TOKENS and not next_w.isdigit() and len(next_w) >= 3:
                bound_attr = next_norm

        # Identify candidate entity in immediate preceding window (up to 5 tokens before)
        entity_tokens = []
        entity_search_start = max(0, num_tok_idx - 5)
        for idx in range(entity_search_start, num_tok_idx):
            tok = tokens[idx][0]
            if (tok[0].isupper() or (entity_tokens and tok.isupper())) and tok.lower() not in STOP_TOKENS:
                entity_tokens.append(tok)
            elif entity_tokens:
                if tok.lower() in STOP_TOKENS and len(tok) <= 3:
                    continue
                entity_tokens = []
        if entity_tokens:
            bound_entity = " ".join(entity_tokens)

        # Fallback attribute: if no explicit attribute noun found, use nearest non-stop content word
        if not bound_attr:
            for idx in range(max(0, num_tok_idx - 4), min(len(tokens), num_tok_idx + 5)):
                if idx == num_tok_idx:
                    continue
                w = tokens[idx][0]
                if w.lower() not in STOP_TOKENS and not w.isdigit() and len(w) >= 3:
                    bound_attr = normalize_token(w)
                    break

        window_str = clean_text[tokens[window_start][1]: tokens[window_end - 1][2]]

        slots.append(FactSlot(
            attribute=bound_attr or "general_quantity",
            number=num,
            entity=bound_entity,
            qualifier=qualifier,
            window_text=window_str
        ))

    return slots


class SlotComparisonResult:
    def __init__(
        self,
        has_slot_clash: bool = False,
        has_slot_match: bool = False,
        reasons: Optional[List[str]] = None
    ):
        self.has_slot_clash = has_slot_clash
        self.has_slot_match = has_slot_match
        self.reasons = reasons or []


def compare_fact_slots(
    claim_slots: List[FactSlot],
    evidence_slots: List[FactSlot]
) -> SlotComparisonResult:
    """
    Compare claim fact slots against evidence fact slots.
    Compares values ONLY when the attribute (and entity if present) matches!
    """
    reasons: List[str] = []
    has_clash = False
    has_match = False

    if not claim_slots or not evidence_slots:
        return SlotComparisonResult()

    # Index evidence slots by normalized attribute
    evidence_by_attr: Dict[str, List[FactSlot]] = {}
    for es in evidence_slots:
        evidence_by_attr.setdefault(es.attribute, []).append(es)

    for cs in claim_slots:
        # Check if evidence discusses this exact attribute
        if cs.attribute in evidence_by_attr:
            matching_attrs = evidence_by_attr[cs.attribute]
            value_matched = False
            conflicting_values = []

            for es in matching_attrs:
                # If both have entities specified, ensure entity compatibility
                if cs.entity and es.entity and cs.entity != es.entity:
                    continue

                if cs.number.equals(es.number):
                    value_matched = True
                    has_match = True
                    reasons.append(
                        f"Matching numerical value verified on '{cs.attribute}': {cs.number.raw_text}"
                    )
                    break
                else:
                    conflicting_values.append(es.number.raw_text)

            if not value_matched and conflicting_values:
                has_clash = True
                reasons.append(
                    f"Numerical mismatch on '{cs.attribute}': claim states {cs.number.raw_text}, source states {', '.join(conflicting_values)}"
                )

    return SlotComparisonResult(
        has_slot_clash=has_clash,
        has_slot_match=has_match,
        reasons=reasons
    )
