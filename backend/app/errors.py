"""
Standardized error codes, exceptions, and HTTP response mappings.
"""
from enum import Enum
from fastapi import HTTPException, status

class ErrorCode(str, Enum):
    ANSWER_EMPTY = "ANSWER_EMPTY"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    CONTENT_TOO_LARGE = "CONTENT_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    SOURCE_EMPTY_OR_UNREADABLE = "SOURCE_EMPTY_OR_UNREADABLE"
    INVALID_INPUT = "INVALID_INPUT"
    RATE_LIMITED = "RATE_LIMITED"
    AUDIT_FAILED = "AUDIT_FAILED"

class WarningCode(str, Enum):
    MODEL_FALLBACK_RULES_ONLY = "MODEL_FALLBACK_RULES_ONLY"
    DOCUMENT_TRUNCATED = "DOCUMENT_TRUNCATED"
    PAGE_METADATA_UNAVAILABLE = "PAGE_METADATA_UNAVAILABLE"
    UNVERIFIED_PARAPHRASE = "UNVERIFIED_PARAPHRASE"

class SecondOpinionException(HTTPException):
    def __init__(self, error_code: ErrorCode, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(
            status_code=status_code,
            detail={"code": error_code.value, "message": message}
        )
