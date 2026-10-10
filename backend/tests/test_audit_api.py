"""
Integration tests for the Audit API (POST /api/audits, export).
"""
import io
from pathlib import Path
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from docx import Document as DocxDocument

from backend.app.main import app
from backend.app.errors import ErrorCode

client = TestClient(app)
FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_audit_api_plain_text():
    policy_text = (FIXTURES_DIR / "sample_policy.txt").read_text(encoding="utf-8")
    answer = "Employees can receive up to $500 for home office equipment. Monthly internet is $100."

    response = client.post(
        "/api/audits",
        data={
            "answer": answer,
            "source_text": policy_text
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert data["audit_id"].startswith("audit_")
    assert data["original_answer"] == answer
    assert len(data["sources"]) == 1
    assert data["sources"][0]["filename"] == "pasted_source.txt"
    assert len(data["findings"]) == 2

    # Check verdicts
    findings = data["findings"]
    assert findings[0]["verdict"] == "SUPPORTED_BY_SOURCE"
    assert findings[1]["verdict"] == "NOT_ESTABLISHED_BY_SOURCE"

    # Check summary
    summary = data["summary"]
    assert summary["total_claims"] == 2
    assert summary["supported_claims"] == 1
    assert summary["not_established_claims"] == 1

def test_audit_api_file_upload_pdf_and_docx():
    # Build in-memory PDF with pypdf
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    pdf_buf = io.BytesIO()
    writer.write(pdf_buf)
    pdf_bytes = pdf_buf.getvalue()

    # Build in-memory DOCX
    docx_doc = DocxDocument()
    docx_doc.add_paragraph("Remote employees are reimbursed $500 for equipment.")
    docx_buf = io.BytesIO()
    docx_doc.save(docx_buf)
    docx_bytes = docx_buf.getvalue()

    response = client.post(
        "/api/audits",
        data={"answer": "Employees receive $500 for equipment."},
        files=[
            ("files", ("test_policy.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ]
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) == 1
    assert data["sources"][0]["filename"] == "test_policy.docx"
    assert data["findings"][0]["verdict"] == "SUPPORTED_BY_SOURCE"

def test_audit_api_validation_errors():
    # 1. Empty answer
    res1 = client.post("/api/audits", data={"answer": "   ", "source_text": "Some source"})
    assert res1.status_code == 400
    assert res1.json()["detail"]["code"] == ErrorCode.ANSWER_EMPTY.value

    # 2. Empty sources (no text and no files)
    res2 = client.post("/api/audits", data={"answer": "A valid claim."})
    assert res2.status_code == 400
    assert res2.json()["detail"]["code"] == ErrorCode.SOURCE_EMPTY_OR_UNREADABLE.value

    # 3. Unsupported file type
    res3 = client.post(
        "/api/audits",
        data={"answer": "A valid claim."},
        files=[("files", ("script.sh", b"echo hello", "text/x-sh"))]
    )
    assert res3.status_code == 400
    assert res3.json()["detail"]["code"] == ErrorCode.UNSUPPORTED_FILE_TYPE.value

def test_markdown_export():
    policy_text = (FIXTURES_DIR / "sample_policy.txt").read_text(encoding="utf-8")
    answer = "Employees receive up to $500 for equipment."

    audit_res = client.post(
        "/api/audits",
        data={"answer": answer, "source_text": policy_text}
    )
    audit_data = audit_res.json()

    export_res = client.post("/api/audits/export/markdown", json=audit_data)
    assert export_res.status_code == 200
    assert export_res.headers["content-type"].startswith("text/markdown")
    content = export_res.text
    assert "# Second Opinion — Audit Report" in content
    assert "Executive Summary" in content
    assert "SUPPORTED_BY_SOURCE" in content
    assert "Disclaimer" in content
