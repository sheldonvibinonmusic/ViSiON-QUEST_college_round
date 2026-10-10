"""
FastAPI route definitions for health and auditing endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Form, File, UploadFile, Response
from backend.app.config import settings
from backend.app.schemas import HealthResponse, SystemLimits, VerifierMode, AuditResponse
from backend.app.services.audit_service import process_audit, generate_markdown_report

router = APIRouter(prefix="/api", tags=["audit"])

@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """
    Returns system readiness, active verifier mode, model status, and limits.
    """
    limits = SystemLimits(
        max_answer_chars=settings.MAX_ANSWER_CHARS,
        max_source_chars=settings.MAX_SOURCE_CHARS,
        max_files=settings.MAX_FILES,
        max_file_bytes=settings.MAX_FILE_BYTES,
        max_claims=settings.MAX_CLAIMS,
    )
    
    return HealthResponse(
        status="ok",
        version="0.1.0",
        verifier_mode=VerifierMode.RULES_AND_MODEL if settings.MODEL_ENABLED else VerifierMode.RULES_ONLY,
        model_loaded=False,
        model_id=settings.MODEL_ID,
        supported_file_types=settings.SUPPORTED_FILE_EXTENSIONS,
        limits=limits,
    )

@router.post("/audits", response_model=AuditResponse)
async def create_audit(
    answer: str = Form(...),
    source_text: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
) -> AuditResponse:
    """
    Run a source-grounded audit synchronously against provided source text and/or files.
    """
    return await process_audit(
        answer=answer,
        source_text=source_text,
        files=files
    )

@router.post("/audits/export/markdown")
def export_audit_markdown(audit: AuditResponse) -> Response:
    """
    Export the audit report as a downloadable Markdown document.
    """
    markdown_content = generate_markdown_report(audit)
    filename = f"second_opinion_audit_{audit.audit_id}.md"
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
