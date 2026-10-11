"""
Main FastAPI entry point for Second Opinion.
Configures CORS, registers routes, and sets up health and audit APIs.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.audit_routes import router as audit_router

app = FastAPI(
    title="Second Opinion API",
    description="Evidence-Grounded AI Answer Auditor API",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(audit_router)

from fastapi.responses import JSONResponse
from fastapi import Request
from backend.app.errors import SecondOpinionException, ErrorCode

@app.exception_handler(SecondOpinionException)
async def second_opinion_exception_handler(request: Request, exc: SecondOpinionException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": {"code": ErrorCode.AUDIT_FAILED.value, "message": f"Internal server error: {str(exc)}"}}
    )


@app.get("/")
def root():
    return {
        "message": "Second Opinion API is running. Check /api/health for system status."
    }
