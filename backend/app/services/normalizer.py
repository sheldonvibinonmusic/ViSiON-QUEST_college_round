"""
Text and numerical normalization module for Second Opinion.
Provides deterministic unicode cleanup, number/currency/unit equivalence mapping,
lightweight stemmer, and abbreviation/synonym expansion.
"""
import re
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

# Common abbreviations and domain synonyms
ABBREVIATIONS_MAP: Dict[str, str] = {
    "ceo": "chief executive officer",
    "cfo": "chief financial officer",
    "cto": "chief technology officer",
    "us": "united states",
    "usa": "united states",
    "uk": "united kingdom",
    "eu": "european union",
    "un": "united nations",
    "approx": "approximately",
    "dept": "department",
    "govt": "government",
    "yr": "year",
    "yrs": "years",
    "mo": "month",
    "mos": "months",
    "hr": "hour",
    "hrs": "hours",
    "min": "minimum",
    "max": "maximum",
    "rev": "revenue",
    "exp": "expenses",
    "pct": "percent",
    "dr": "doctor",
    "prof": "professor",
}

# Synonyms for directional and scale concepts
SYNONYM_MAP: Dict[str, str] = {
    "rise": "increase",
    "rose": "increase",
    "grow": "increase",
    "grew": "increase",
    "growth": "increase",
    "gain": "increase",
    "gained": "increase",
    "drop": "decrease",
    "dropped": "decrease",
    "fall": "decrease",
    "fell": "decrease",
    "decline": "decrease",
    "declined": "decrease",
    "loss": "decrease",
    "lost": "decrease",
    "shrink": "decrease",
    "shrank": "decrease",
    "huge": "large",
    "massive": "large",
    "tiny": "small",
    "minimal": "small",
    "purchase": "buy",
    "purchased": "buy",
    "procure": "buy",
    "procured": "buy",
    "reimburse": "reimburse",
    "reimbursed": "reimburse",
    "reimbursement": "reimburse",
}

NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}

MULTIPLIERS = {
    "hundred": 100,
    "thousand": 1_000,
    "k": 1_000,
    "million": 1_000_000,
    "m": 1_000_000,
    "billion": 1_000_000_000,
    "b": 1_000_000_000,
    "trillion": 1_000_000_000_000,
    "t": 1_000_000_000_000,
}

ORDINALS = {
    "first": 1, "1st": 1,
    "second": 2, "2nd": 2,
    "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4,
    "fifth": 5, "5th": 5,
    "sixth": 6, "6th": 6,
    "seventh": 7, "7th": 7,
    "eighth": 8, "8th": 8,
    "ninth": 9, "9th": 9,
    "tenth": 10, "10th": 10,
}


def clean_unicode_and_whitespace(text: str) -> str:
    """Normalize unicode to NFKC, unescape special quotes/dashes, clean spaces."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFKC", text)
    # Replace smart quotes and dashes
    norm = norm.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    norm = norm.replace("—", " - ").replace("–", " - ").replace("−", "-")
    norm = re.sub(r"[ \t]+", " ", norm)
    return norm.strip()


class NormalizedNumber:
    """Canonical representation of a numeric/currency/percentage quantity."""
    def __init__(
        self,
        value: float,
        unit: str = "",
        raw_text: str = "",
        start_char: int = -1,
        end_char: int = -1
    ):
        self.value = value
        self.unit = unit
        self.raw_text = raw_text
        self.start_char = start_char
        self.end_char = end_char

    def __repr__(self):
        return f"NormalizedNumber({self.value}, unit='{self.unit}', raw='{self.raw_text}')"

    def equals(self, other: "NormalizedNumber", rel_tol: float = 1e-4) -> bool:
        """Check if two normalized numbers match in value and compatible unit."""
        if not isinstance(other, NormalizedNumber):
            return False
        # Unit compatibility: both empty, or both currency ('$' vs '$'), or both percent ('%')
        if self.unit and other.unit and self.unit != other.unit:
            return False
        # Exact integer match or relative float tolerance
        if abs(self.value - other.value) <= max(1e-5, rel_tol * max(abs(self.value), abs(other.value))):
            return True
        return False


def parse_normalized_numbers(text: str) -> List[NormalizedNumber]:
    """
    Extract and normalize all numbers, currencies, percentages, and multipliers.
    Equates '$45M' == '45 million' == '45,000,000' == '$45,000,000'.
    """
    results: List[NormalizedNumber] = []
    cleaned = clean_unicode_and_whitespace(text)

    # Pattern 1: Currency symbols followed by number and optional multiplier ($45M, $45 million, $45,000,000)
    # e.g., $ 45 million, € 12.5M, £ 100k, $45M
    currency_pat = re.compile(
        r'([$€£¥])\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|thousand|[kmbt])?\b',
        re.IGNORECASE
    )
    for m in currency_pat.finditer(cleaned):
        curr_sym = m.group(1)
        num_str = m.group(2).replace(",", "")
        mult_str = (m.group(3) or "").lower()
        val = float(num_str)
        if mult_str in MULTIPLIERS:
            val *= MULTIPLIERS[mult_str]
        results.append(NormalizedNumber(
            value=val,
            unit="$" if curr_sym in ("$", "€", "£", "¥") else curr_sym,
            raw_text=m.group(0),
            start_char=m.start(),
            end_char=m.end()
        ))

    # Pattern 2: Number followed by word currency / multipliers (45 million dollars, 45 million, 45,000,000)
    # Avoid duplicate matches already consumed by currency_pat
    consumed_spans = [(r.start_char, r.end_char) for r in results]

    def is_consumed(start, end):
        return any(s <= start and end <= e for s, e in consumed_spans)

    num_mult_pat = re.compile(
        r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|thousand|[kmbt])?\s*(dollars|usd|eur|gbp|percent|%|degrees|celsius|fahrenheit|meters|miles|km|hours|days|years)?\b',
        re.IGNORECASE
    )
    for m in num_mult_pat.finditer(cleaned):
        if is_consumed(m.start(), m.end()):
            continue
        num_str = m.group(1).replace(",", "")
        mult_str = (m.group(2) or "").lower()
        unit_str = (m.group(3) or "").lower()

        val = float(num_str)
        if mult_str in MULTIPLIERS:
            val *= MULTIPLIERS[mult_str]

        unit = ""
        if unit_str in ("dollars", "usd"):
            unit = "$"
        elif unit_str in ("percent", "%"):
            unit = "%"
        elif unit_str in ("degrees", "celsius", "fahrenheit"):
            unit = "temp"
        elif unit_str:
            unit = unit_str

        results.append(NormalizedNumber(
            value=val,
            unit=unit,
            raw_text=m.group(0),
            start_char=m.start(),
            end_char=m.end()
        ))
        consumed_spans.append((m.start(), m.end()))

    # Pattern 3: Word numbers (e.g., 'forty-five million')
    word_num_pat = re.compile(
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:\s+(one|two|three|four|five|six|seven|eight|nine))?\s+(million|billion|trillion|thousand)\b',
        re.IGNORECASE
    )
    for m in word_num_pat.finditer(cleaned):
        if is_consumed(m.start(), m.end()):
            continue
        w1 = m.group(1).lower()
        w2 = (m.group(2) or "").lower()
        mult = (m.group(3) or "").lower()
        base_val = NUMBER_WORDS.get(w1, 0) + NUMBER_WORDS.get(w2, 0)
        val = base_val * MULTIPLIERS.get(mult, 1)
        results.append(NormalizedNumber(
            value=float(val),
            unit="",
            raw_text=m.group(0),
            start_char=m.start(),
            end_char=m.end()
        ))

    return results


def stem_word(word: str) -> str:
    """
    Lightweight, deterministic suffix stemmer in pure Python.
    Normalizes plurals, tenses (-ed, -ing), and agentive/nominal derivations (-ment, -tion).
    """
    w = word.lower().strip()
    if len(w) <= 3:
        return w

    # Step 1: Plurals and s
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("s") and not w.endswith("ss") and not w.endswith("us") and not w.endswith("is"):
        w = w[:-1]

    # Step 2: Past tense and progressive
    if w.endswith("ing") and len(w) > 5:
        w = w[:-3]
        if len(w) > 2 and w[-1] == w[-2] and w[-1] not in "lsz":
            w = w[:-1]
    elif w.endswith("ed") and len(w) > 4:
        w = w[:-2]
        if len(w) > 2 and w[-1] == w[-2] and w[-1] not in "lsz":
            w = w[:-1]

    # Step 3: Derivations
    if w.endswith("ment") and len(w) > 6:
        w = w[:-4]
    elif w.endswith("tion") and len(w) > 6:
        w = w[:-4] + "t"
    elif w.endswith("able") and len(w) > 6:
        w = w[:-4]
    elif w.endswith("ibility") and len(w) > 8:
        w = w[:-7]

    return w


def normalize_token(token: str) -> str:
    """Apply abbreviation expansion, synonym mapping, and stemming to a single token."""
    t = token.lower().strip()
    if not t:
        return ""
    if t in ABBREVIATIONS_MAP:
        return ABBREVIATIONS_MAP[t]
    if t in SYNONYM_MAP:
        return SYNONYM_MAP[t]
    return stem_word(t)


def normalize_sentence(sentence: str) -> str:
    """Clean and normalize sentence tokens while expanding abbreviations and synonyms."""
    clean = clean_unicode_and_whitespace(sentence)
    tokens = re.findall(r"\b[A-Za-z0-9_-]+\b", clean)
    normalized_tokens = [normalize_token(t) for t in tokens if t]
    return " ".join(normalized_tokens)
