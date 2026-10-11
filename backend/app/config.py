"""
Configuration and runtime environment settings for Second Opinion.
Strictly local-first with zero mandatory external API keys.
"""
from typing import List
import os
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS: Allow frontend Vite dev server, preview, and local host
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:4173,http://127.0.0.1:4173"
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
    MAX_TEXT_CHARS: int = int(os.getenv("MAX_TEXT_CHARS", "50000000"))
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "50"))
    MAX_FILES: int = int(os.getenv("MAX_FILES", "5"))
    MAX_FILE_BYTES: int = int(os.getenv("MAX_FILE_BYTES", str(10 * 1024 * 1024)))  # 10 MiB
    MAX_CLAIMS: int = int(os.getenv("MAX_CLAIMS", "50"))

    # Supported File Types for Source Extraction
    SUPPORTED_FILE_EXTENSIONS: List[str] = [".txt", ".pdf", ".docx"]

    # Source Fit Check Settings (Default OFF)
    SOURCE_FIT_ENABLED: bool = os.getenv("SOURCE_FIT_ENABLED", "false").lower() in ("true", "1", "yes")
    SOURCE_FIT_OFF_TOPIC_THRESHOLD: float = float(os.getenv("SOURCE_FIT_OFF_TOPIC_THRESHOLD", "0.15"))
    SOURCE_FIT_RELEVANT_THRESHOLD: float = float(os.getenv("SOURCE_FIT_RELEVANT_THRESHOLD", "0.45"))

    # URL Ingestion Settings (Default OFF)
    URL_INGESTION_ENABLED: bool = os.getenv("URL_INGESTION_ENABLED", "false").lower() in ("true", "1", "yes")
    MAX_URLS: int = int(os.getenv("MAX_URLS", "5"))
    URL_MAX_BYTES: int = int(os.getenv("URL_MAX_BYTES", str(2 * 1024 * 1024)))
    URL_TIMEOUT_SECONDS: float = float(os.getenv("URL_TIMEOUT_SECONDS", "5.0"))

    # Free Web Evidence & Fallback Settings (Default OFF)
    WEB_EVIDENCE_ENABLED: bool = os.getenv("WEB_EVIDENCE_ENABLED", "false").lower() in ("true", "1", "yes")
    MAX_WEB_QUERIES_PER_AUDIT: int = int(os.getenv("MAX_WEB_QUERIES_PER_AUDIT", "5"))
    WEB_CACHE_TTL_SECONDS: int = int(os.getenv("WEB_CACHE_TTL_SECONDS", "900"))

    # Optional External Search API Keys (Keyless operation works when None)
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")
    SERPER_API_KEY: str | None = os.getenv("SERPER_API_KEY")
    OPENALEX_API_KEY: str | None = os.getenv("OPENALEX_API_KEY")
    CROSSREF_MAILTO: str = os.getenv("CROSSREF_MAILTO", "auditor@secondopinion.local")

    # Optional Local Verifier Model (Default OFF)
    MINICHECK_ENABLED: bool = os.getenv("MINICHECK_ENABLED", "false").lower() in ("true", "1", "yes")

settings = Settings()
