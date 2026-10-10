"""
Tests for deterministic claim segmentation and Unicode offset preservation.
Invariants verified:
1. answer[claim.start_char:claim.end_char] == claim.text for all claims
2. Abbreviations and decimals do not cause false sentence boundaries
"""
import pytest
from backend.app.services.claim_segmenter import segment_claims
from backend.app.util.offsets import verify_span_match, validate_span, calculate_char_coverage
from backend.app.errors import SecondOpinionException, ErrorCode

def test_basic_sentence_splitting_and_offsets():
    answer = "First claim is here. Second claim follows! Third claim is a question?"
    claims = segment_claims(answer)
    
    assert len(claims) == 3
    for claim in claims:
        # Crucial invariant: exact slice into answer matches claim.text
        assert answer[claim.start_char:claim.end_char] == claim.text
        assert verify_span_match(answer, claim.start_char, claim.end_char, claim.text)

    assert claims[0].text == "First claim is here."
    assert claims[1].text == "Second claim follows!"
    assert claims[2].text == "Third claim is a question?"

def test_abbreviation_and_decimal_handling():
    answer = "Dr. Adams stated that revenue grew by 4.5% in Q3. This was confirmed by Prof. Higgins."
    claims = segment_claims(answer)
    
    # Should be 2 sentences, not split at Dr. or 4.5% or Prof.
    assert len(claims) == 2
    for claim in claims:
        assert answer[claim.start_char:claim.end_char] == claim.text

    assert "Dr. Adams stated that revenue grew by 4.5% in Q3." == claims[0].text
    assert "This was confirmed by Prof. Higgins." == claims[1].text

def test_quotes_and_newlines():
    answer = 'The analyst said, "Growth remains stable." \n\nHowever, inflation rose.'
    claims = segment_claims(answer)
    
    assert len(claims) == 2
    for claim in claims:
        assert answer[claim.start_char:claim.end_char] == claim.text

    assert claims[0].text == 'The analyst said, "Growth remains stable."'
    assert claims[1].text == 'However, inflation rose.'

def test_unicode_and_special_characters():
    answer = "Modèle vérifié avec précision. Coût total: 100€! Tout va bien."
    claims = segment_claims(answer)
    
    assert len(claims) == 3
    for claim in claims:
        assert answer[claim.start_char:claim.end_char] == claim.text

def test_empty_answer_raises_error():
    with pytest.raises(SecondOpinionException) as exc_info:
        segment_claims("   \n\t  ")
    assert exc_info.value.detail["code"] == ErrorCode.ANSWER_EMPTY.value

def test_max_claims_cap():
    answer = " ".join([f"Sentence {i} is here." for i in range(20)])
    claims = segment_claims(answer, max_claims=5)
    assert len(claims) == 5
    for claim in claims:
        assert answer[claim.start_char:claim.end_char] == claim.text

def test_calculate_char_coverage():
    assert calculate_char_coverage(100, [(0, 50), (60, 80)]) == 0.7
    assert calculate_char_coverage(0, [(0, 10)]) == 0.0
    assert calculate_char_coverage(50, []) == 0.0
    assert calculate_char_coverage(50, [(0, 50)]) == 1.0

