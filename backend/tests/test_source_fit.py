"""
Tests for Source Fit Check service and integration into the audit pipeline.
Verifies domain/topical alignment grading and prevention of false contradictions on off-topic sources.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas import (
    SourceFitLevel,
    FactualVerdict,
    SourceDocument,
    SourceChunk,
    Claim,
)
from backend.app.services.source_fit import check_source_fit, extract_salient_terms
from backend.app.services.audit_service import process_audit, generate_markdown_report

client = TestClient(app)

def test_extract_salient_terms():
    text = "Albert Einstein formulated the theory of general relativity and predicted gravitational waves in 1915."
    terms = extract_salient_terms(text)
    assert "albert" in terms
    assert "einstein" in terms
    assert "relativity" in terms
    assert "gravitational" in terms
    assert "waves" in terms
    # Stopwords should not be present
    assert "the" not in terms
    assert "of" not in terms
    assert "and" not in terms

def test_source_fit_relevant():
    answer = "Quantum entanglement occurs when pairs of particles interact such that quantum states cannot be described independently."
    claims = [
        Claim(claim_id="c1", text="Quantum entanglement involves pairs of particles.", start_char=0, end_char=50),
        Claim(claim_id="c2", text="Quantum states cannot be described independently.", start_char=51, end_char=100)
    ]
    doc = SourceDocument(
        source_id="src_1",
        filename="quantum_physics.txt",
        media_type="text/plain",
        sha256="abc12345",
        character_count=500,
        page_count=1
    )
    chunks = [
        SourceChunk(
            chunk_id="chk_1",
            source_id="src_1",
            text="In quantum mechanics, quantum entanglement is a phenomenon where pairs of particles share entangled quantum states.",
            start_char=0,
            end_char=120
        )
    ]

    fit = check_source_fit(answer, claims, chunks, [doc])
    assert fit.overall_fit in (SourceFitLevel.RELEVANT, SourceFitLevel.PARTIALLY_RELEVANT)
    assert not fit.all_sources_off_topic
    assert fit.documents[0].fit_score >= 0.40

def test_source_fit_off_topic():
    answer = "General relativity explains gravitational time dilation and the curvature of spacetime around massive celestial bodies."
    claims = [
        Claim(claim_id="c1", text="General relativity explains gravitational time dilation.", start_char=0, end_char=60),
        Claim(claim_id="c2", text="Spacetime curves around massive celestial bodies.", start_char=61, end_char=110)
    ]
    doc = SourceDocument(
        source_id="src_culinary",
        filename="french_pastry_recipes.txt",
        media_type="text/plain",
        sha256="def67890",
        character_count=400,
        page_count=1
    )
    chunks = [
        SourceChunk(
            chunk_id="chk_pastry",
            source_id="src_culinary",
            text="To prepare laminated croissant dough, incorporate unsalted butter at room temperature and fold three times.",
            start_char=0,
            end_char=110
        )
    ]

    fit = check_source_fit(answer, claims, chunks, [doc])
    assert fit.overall_fit == SourceFitLevel.OFF_TOPIC
    assert fit.all_sources_off_topic is True
    assert fit.documents[0].fit_level == SourceFitLevel.OFF_TOPIC
    assert fit.documents[0].fit_score < 0.15
    assert len(fit.documents[0].missing_topics) > 0

@pytest.mark.anyio
async def test_audit_off_topic_prevents_false_contradiction():
    """
    Core Product Requirement:
    A domain mismatch must NOT falsely label claims as contradicted.
    Instead, it must label claims as NOT_ESTABLISHED_BY_SOURCE with a domain mismatch explanation.
    """
    physics_answer = (
        "Albert Einstein published his paper on general relativity in 1915. "
        "Gravitational waves propagate through the vacuum of space at exactly the speed of light."
    )
    baking_source = (
        "Classic sourdough bread requires wild yeast and lactic acid bacteria fermentation. "
        "Bake the loaf in a preheated Dutch oven at 230 degrees Celsius for 25 minutes."
    )

    response = await process_audit(
        answer=physics_answer,
        source_text=baking_source,
        check_source_fit_flag=True
    )

    assert response.source_fit is not None
    assert response.source_fit.all_sources_off_topic is True
    assert response.source_fit.overall_fit == SourceFitLevel.OFF_TOPIC

    # Must have warnings
    assert any("off-topic" in w.lower() for w in response.warnings)

    # Every single claim must be NOT_ESTABLISHED_BY_SOURCE, NOT CONTRADICTED
    for finding in response.findings:
        assert finding.verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE
        assert "Source does not cover this topic" in finding.explanation
        assert "Unverified due to domain mismatch, not false" in finding.explanation
        assert finding.evidence == []

    # Markdown report contains the Source Fit section
    report = generate_markdown_report(response)
    assert "## Source Fit Assessment" in report
    assert "OFF_TOPIC" in report

def test_api_audit_with_check_source_fit():
    """
    Verify POST /api/audits route accepts check_source_fit and min_source_fit_score form fields.
    """
    physics_answer = "Electrons orbit the nucleus at discrete quantized energy levels."
    gardening_source = "Perennial shrubs need well-draining soil and prune dead branches in early spring."

    response = client.post(
        "/api/audits",
        data={
            "answer": physics_answer,
            "source_text": gardening_source,
            "check_source_fit": "true",
            "min_source_fit_score": "0.2"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "source_fit" in data
    assert data["source_fit"] is not None
    assert data["source_fit"]["all_sources_off_topic"] is True
    assert all(f["verdict"] == "NOT_ESTABLISHED_BY_SOURCE" for f in data["findings"])

def test_api_audit_backward_compatibility():
    """
    Verify that existing API calls without source fit parameters continue working exactly as before.
    """
    answer = "The boiling point of water at sea level is 100 degrees Celsius."
    source = "Water boils at 100 degrees Celsius at 1 atmosphere of pressure."

    response = client.post(
        "/api/audits",
        data={
            "answer": answer,
            "source_text": source
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["findings"]) > 0
    # source_fit can be None when not requested and SOURCE_FIT_ENABLED=False
    assert "audit_id" in data
    assert "original_answer" in data
