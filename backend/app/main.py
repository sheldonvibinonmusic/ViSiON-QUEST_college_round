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

@app.get("/")
def root():
    return {
        "message": "Second Opinion API is running. Check /api/health for system status."
    }
