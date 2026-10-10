"""
Tests for Web URL Ingestion and Strict SSRF Defense Service.
Verifies IP validation (loopback, private, link-local metadata), HTML extraction, and audit integration.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.errors import SecondOpinionException, ErrorCode
from backend.app.services.url_fetcher import (
    validate_url_and_check_ssrf,
    HTMLContentExtractor,
    fetch_and_parse_url,
)
from backend.app.services.audit_service import process_audit

client = TestClient(app)

def test_scheme_validation():
    # Only http and https permitted
    with pytest.raises(SecondOpinionException) as exc1:
        validate_url_and_check_ssrf("file:///etc/passwd")
    assert exc1.value.detail["code"] == ErrorCode.INVALID_INPUT.value

    with pytest.raises(SecondOpinionException) as exc2:
        validate_url_and_check_ssrf("ftp://example.com/file.txt")
    assert exc2.value.detail["code"] == ErrorCode.INVALID_INPUT.value

    with pytest.raises(SecondOpinionException) as exc3:
        validate_url_and_check_ssrf("data:text/html,<html>test</html>")
    assert exc3.value.detail["code"] == ErrorCode.INVALID_INPUT.value

def test_ssrf_blocking_loopback_and_metadata():
    # Loopback IP
    with pytest.raises(SecondOpinionException) as exc1:
        validate_url_and_check_ssrf("http://127.0.0.1:8000/secret")
    assert exc1.value.detail["code"] == ErrorCode.INVALID_INPUT.value
    assert "blocked private, loopback, or metadata IP" in exc1.value.detail["message"]

    # Localhost
    with pytest.raises(SecondOpinionException) as exc2:
        validate_url_and_check_ssrf("http://localhost:5000/internal")
    assert exc2.value.detail["code"] == ErrorCode.INVALID_INPUT.value

    # Cloud Metadata (AWS/GCP: 169.254.169.254)
    with pytest.raises(SecondOpinionException) as exc3:
        validate_url_and_check_ssrf("http://169.254.169.254/latest/meta-data/")
    assert exc3.value.detail["code"] == ErrorCode.INVALID_INPUT.value

    # RFC 1918 Private Ranges
    with pytest.raises(SecondOpinionException) as exc4:
        validate_url_and_check_ssrf("http://192.168.1.1/admin")
    assert exc4.value.detail["code"] == ErrorCode.INVALID_INPUT.value

    with pytest.raises(SecondOpinionException) as exc5:
        validate_url_and_check_ssrf("http://10.0.0.1/dashboard")
    assert exc5.value.detail["code"] == ErrorCode.INVALID_INPUT.value

def test_html_content_extractor():
    sample_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Quantum Mechanics Primer</title>
        <style>body { color: red; }</style>
        <script>alert("hack");</script>
      </head>
      <body>
        <nav><a href="/home">Home</a></nav>
        <header>Header content</header>
        <article>
          <h1>Introduction to Quantum Physics</h1>
          <p>Quantum entanglement occurs when subatomic particles become correlated.</p>
          <p>Even across vast cosmic distances, the states remain interdependent.</p>
        </article>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    extractor = HTMLContentExtractor()
    extractor.feed(sample_html)
    title, text = extractor.get_extracted_text()

    assert title == "Quantum Mechanics Primer"
    assert "alert" not in text
    assert "body { color" not in text
    assert "Home" not in text
    assert "Copyright 2026" not in text
    assert "Introduction to Quantum Physics" in text
    assert "Quantum entanglement occurs when subatomic particles become correlated." in text

@pytest.mark.anyio
async def test_fetch_and_parse_url_mocked():
    html_page = """
    <html>
      <head><title>Black Hole Physics</title></head>
      <body>
        <h1>Event Horizon</h1>
        <p>The event horizon is a boundary beyond which events cannot affect an observer.</p>
      </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = html_page.encode("utf-8")

    with patch("backend.app.services.url_fetcher.validate_url_and_check_ssrf"):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            doc, chunks = await fetch_and_parse_url("https://science.example.com/black-holes")
            assert doc.media_type == "text/html"
            assert "Black Hole Physics" in doc.filename
            assert len(chunks) > 0
            assert "event horizon" in chunks[0].text.lower()

@pytest.mark.anyio
async def test_audit_with_user_url():
    """
    Verifies that supplying a web URL as an audit source:
    1. Ingests the page content.
    2. Tags evidence provenance as 'user_url' with origin source_url.
    """
    html_page = """
    <html>
      <head><title>Mars Exploration</title></head>
      <body>
        <p>Mars has two small natural satellites named Phobos and Deimos.</p>
      </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = html_page.encode("utf-8")

    with patch("backend.app.services.url_fetcher.validate_url_and_check_ssrf"):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            response = await process_audit(
                answer="Mars has two natural moons known as Phobos and Deimos.",
                urls="https://science.example.com/mars"
            )

            assert len(response.sources) > 0
            assert response.sources[0].media_type == "text/html"
            assert len(response.findings) > 0

            evi = response.findings[0].evidence[0]
            assert evi.origin_type == "user_url"
            assert evi.source_url == "https://science.example.com/mars"

def test_api_audit_with_urls_form_param():
    """
    Verify POST /api/audits route accepts 'urls' form field.
    """
    html_page = """
    <html>
      <head><title>Jupiter Moons</title></head>
      <body>
        <p>Jupiter is orbited by numerous moons including Europa, Ganymede, Callisto, and Io.</p>
      </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = html_page.encode("utf-8")

    with patch("backend.app.services.url_fetcher.validate_url_and_check_ssrf"):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            response = client.post(
                "/api/audits",
                data={
                    "answer": "Jupiter has moons including Europa and Ganymede.",
                    "urls": "https://astronomy.example.com/jupiter"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["sources"]) > 0
            assert data["findings"][0]["evidence"][0]["origin_type"] == "user_url"
