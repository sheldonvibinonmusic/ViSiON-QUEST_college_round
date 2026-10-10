"""
FastAPI route definitions for health and auditing endpoints.
"""
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.schemas import HealthResponse, SystemLimits, VerifierMode

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
        model_loaded=False,  # Updated dynamically when model loader is queried
        model_id=settings.MODEL_ID,
        supported_file_types=settings.SUPPORTED_FILE_EXTENSIONS,
        limits=limits,
    )
