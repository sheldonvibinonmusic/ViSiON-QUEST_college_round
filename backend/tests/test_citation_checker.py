"""
Tests for Citation Support Checker and Independent Sources Corroboration.
Verifies entity, date, and predicate confirmation, and independent corroboration counting.
"""
from backend.app.schemas import Claim, EvidenceReference, FactualVerdict
from backend.app.services.citation_checker import verify_citation_support, extract_named_entities
from backend.app.services.verdict_mapper import map_verdict_for_claim

def test_extract_named_entities():
    text = "The James Webb Space Telescope observed the atmosphere of WASP-96b."
    entities = extract_named_entities(text)
    assert any("james webb" in e for e in entities)
    assert any("wasp-96b" in e.lower() for e in entities)

def test_citation_verified_true():
    claim = "Albert Einstein formulated general relativity in 1915."
    quote = "In November 1915, Albert Einstein completed his general theory of relativity."
    is_verified, reason = verify_citation_support(claim, quote)
    assert is_verified is True
    assert "confirms" in reason.lower()

def test_citation_verified_false_missing_year():
    claim = "The Apollo 11 lunar module landed on the Moon in 1969."
    quote = "The Apollo lunar module landed successfully on the Moon carrying Neil Armstrong."
    # Missing 1969
    is_verified, reason = verify_citation_support(claim, quote)
    assert is_verified is False
    assert "1969" in reason

def test_citation_verified_false_missing_entity():
    claim = "The Hubble Space Telescope confirmed the accelerated expansion of the universe."
    quote = "Space telescopes have confirmed accelerated expansion using type Ia supernovae."
    # Missing Hubble
    is_verified, reason = verify_citation_support(claim, quote)
    assert is_verified is False
    assert "hubble" in reason.lower()

def test_independent_sources_corroboration_multi_source():
    claim = Claim(
        claim_id="c1",
        text="Water boils at 100 degrees Celsius at standard atmospheric pressure.",
        start_char=0,
        end_char=68
    )
    evi1 = EvidenceReference(
        evidence_id="e1",
        source_id="src_doc_1",
        source_name="Chemistry Handbook",
        quote="At 1 atmosphere of pressure, pure water boils at 100 degrees Celsius.",
        start_char=0,
        end_char=70,
        relation="candidate",
        retrieval_rank=1
    )
    evi2 = EvidenceReference(
        evidence_id="e2",
        source_id="src_doc_2",
        source_name="Physics Primer",
        quote="The boiling point of water is 100 degrees Celsius at sea level atmospheric pressure.",
        start_char=0,
        end_char=85,
        relation="candidate",
        retrieval_rank=2
    )

    finding = map_verdict_for_claim(claim, [evi1, evi2])
    assert finding.verdict == FactualVerdict.SUPPORTED_BY_SOURCE
    assert finding.evidence[0].citation_verified is True
    assert finding.evidence[1].citation_verified is True
    # Two distinct sources agree
    assert finding.independent_sources_agreeing == 2

def test_unverified_citation_prevents_false_support():
    claim = Claim(
        claim_id="c2",
        text="The treaty was signed in 1815 in Vienna.",
        start_char=0,
        end_char=40
    )
    evi = EvidenceReference(
        evidence_id="e3",
        source_id="src_history",
        source_name="European History",
        quote="A major peace treaty was negotiated in Vienna following the Napoleonic wars.",  # Missing 1815
        start_char=0,
        end_char=77,
        relation="candidate",
        retrieval_rank=1
    )

    finding = map_verdict_for_claim(claim, [evi])
    # Must NOT be marked supported when critical year is missing from the quote
    assert finding.verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
    assert finding.evidence[0].citation_verified is False
    assert finding.independent_sources_agreeing == 0
