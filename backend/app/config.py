"""
Configuration and runtime environment settings for Second Opinion.
Strictly local-first with zero mandatory external API keys.
"""
from typing import List
import os

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS: Allow frontend Vite dev server and local host
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
        ).split(",")
        if origin.strip()
    ]

    # Model & Verifier Settings
    MODEL_ID: str = os.getenv("MODEL_ID", "microsoft/deberta-base-mnli")
    DEVICE: str = os.getenv("DEVICE", "cpu")
    MODEL_ENABLED: bool = os.getenv("MODEL_ENABLED", "true").lower() in ("true", "1", "yes")

    # Processing and Safety Limits
    MAX_ANSWER_CHARS: int = int(os.getenv("MAX_ANSWER_CHARS", "40000"))
    MAX_SOURCE_CHARS: int = int(os.getenv("MAX_SOURCE_CHARS", "150000"))
    MAX_FILES: int = int(os.getenv("MAX_FILES", "5"))
    MAX_FILE_BYTES: int = int(os.getenv("MAX_FILE_BYTES", str(10 * 1024 * 1024)))  # 10 MiB
    MAX_CLAIMS: int = int(os.getenv("MAX_CLAIMS", "50"))

    # Supported File Types for Source Extraction
    SUPPORTED_FILE_EXTENSIONS: List[str] = [".txt", ".pdf", ".docx"]

settings = Settings()
