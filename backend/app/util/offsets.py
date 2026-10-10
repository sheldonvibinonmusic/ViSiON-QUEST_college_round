"""
Utility functions for Unicode code-point offsets and span validation.
Offsets are zero-based, end-exclusive Unicode code points.
"""
from typing import Tuple

def validate_span(text: str, start_char: int, end_char: int) -> bool:
    """
    Validate that start_char and end_char are within bounds and start_char <= end_char.
    """
    if start_char < 0 or end_char < 0:
        return False
    if start_char > end_char:
        return False
    if end_char > len(text):
        return False
    return True

def slice_span(text: str, start_char: int, end_char: int) -> str:
    """
    Safely slice text between start_char and end_char.
    Raises ValueError if indices are invalid.
    """
    if not validate_span(text, start_char, end_char):
        raise ValueError(
            f"Invalid span [{start_char}:{end_char}] for text of length {len(text)}"
        )
    return text[start_char:end_char]

def verify_span_match(text: str, start_char: int, end_char: int, expected_substring: str) -> bool:
    """
    Confirm that the span in the original text exactly matches the expected substring.
    """
    if not validate_span(text, start_char, end_char):
        return False
    return text[start_char:end_char] == expected_substring

def calculate_char_coverage(total_chars: int, spans: list[Tuple[int, int]]) -> float:
    """
    Compute the fractional coverage of text covered by non-overlapping spans [0.0, 1.0].
    """
    if total_chars <= 0 or not spans:
        return 0.0
    covered_chars = sum(max(0, min(total_chars, end) - max(0, start)) for start, end in spans)
    return min(1.0, covered_chars / total_chars)

