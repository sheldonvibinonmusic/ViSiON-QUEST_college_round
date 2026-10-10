"""
Deterministic claim segmentation service.
Splits an answer into individual claims while strictly preserving original Unicode code-point offsets.
Guarantees: answer[claim.start_char:claim.end_char] == claim.text
"""
import re
from typing import List
from backend.app.schemas import Claim
from backend.app.util.hashes import generate_id
from backend.app.errors import ErrorCode, SecondOpinionException

# Common abbreviations that should NOT trigger a sentence split
ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr",
    "e.g", "i.e", "vs", "etc", "fig", "al", "approx",
    "inc", "ltd", "co", "corp", "no", "vol", "p"
}

def is_abbreviation_or_decimal(text: str, punctuation_pos: int) -> bool:
    """
    Check if the period at punctuation_pos is part of a common abbreviation or decimal number.
    """
    # Check decimal pattern: preceding digit and following digit
    if punctuation_pos + 1 < len(text) and text[punctuation_pos + 1].isdigit():
        if punctuation_pos >= 1 and text[punctuation_pos - 1].isdigit():
            return True

    # Look back for word before period
    pos = punctuation_pos - 1
    while pos >= 0 and (text[pos].isalpha() or text[pos] == '.'):
        pos -= 1
    word = text[pos + 1:punctuation_pos].lower()
    if word in ABBREVIATIONS:
        return True

    return False

def segment_claims(answer: str, max_claims: int = 50) -> List[Claim]:
    """
    Split the unmodified answer string into sentence-level claims.
    Offsets [start_char, end_char] are exact slices into the original answer.
    """
    if not answer or not answer.strip():
        raise SecondOpinionException(
            ErrorCode.ANSWER_EMPTY,
            "Submitted answer text is empty."
        )

    claims: List[Claim] = []
    text_len = len(answer)
    start = 0

    # Pattern matches sentence-ending punctuation optionally followed by closing quotes,
    # followed by whitespace or end of string.
    boundary_pattern = re.compile(r'([.?!])(["\'”’]*)(?=[\s\n\r]|$)', re.UNICODE)

    for match in boundary_pattern.finditer(answer):
        punct = match.group(1)
        punct_pos = match.start(1)
        end = match.end()  # includes trailing quotes if any

        # If it's a period, verify it's not an abbreviation or decimal
        if punct == '.' and is_abbreviation_or_decimal(answer, punct_pos):
            continue

        raw_span = answer[start:end]
        # Trim leading and trailing whitespace while tracking exact offsets into answer
        l_offset = len(raw_span) - len(raw_span.lstrip())
        r_offset = len(raw_span) - len(raw_span.rstrip())

        span_start = start + l_offset
        span_end = end - r_offset
        span_text = answer[span_start:span_end]

        if span_text:
            claims.append(
                Claim(
                    claim_id=generate_id("clm"),
                    text=span_text,
                    start_char=span_start,
                    end_char=span_end,
                    parent_sentence=span_text,
                    compound_claim_review=False,
                    flags=[]
                )
            )

        start = end
        if len(claims) >= max_claims:
            break

    # Handle remaining tail if any
    if start < text_len and len(claims) < max_claims:
        raw_span = answer[start:text_len]
        l_offset = len(raw_span) - len(raw_span.lstrip())
        r_offset = len(raw_span) - len(raw_span.rstrip())
        span_start = start + l_offset
        span_end = text_len - r_offset
        span_text = answer[span_start:span_end]

        if span_text:
            claims.append(
                Claim(
                    claim_id=generate_id("clm"),
                    text=span_text,
                    start_char=span_start,
                    end_char=span_end,
                    parent_sentence=span_text,
                    compound_claim_review=False,
                    flags=[]
                )
            )

    return claims
