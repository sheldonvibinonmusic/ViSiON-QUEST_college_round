"""
Input validation service for audit requests.
Validates character counts, file counts, sizes, extensions, and presence of required inputs.
"""
import os
from typing import List, Optional
from fastapi import UploadFile

from backend.app.config import settings
from backend.app.errors import ErrorCode, SecondOpinionException

def validate_answer(answer: str) -> None:
    """Validate submitted AI-generated answer."""
    if not answer or not answer.strip():
        raise SecondOpinionException(
            ErrorCode.ANSWER_EMPTY,
            "Submitted answer text cannot be empty."
        )

    if len(answer) > settings.MAX_ANSWER_CHARS:
        raise SecondOpinionException(
            ErrorCode.CONTENT_TOO_LARGE,
            f"Answer length ({len(answer)} characters) exceeds maximum allowed limit ({settings.MAX_ANSWER_CHARS})."
        )

def validate_files_metadata(files: Optional[List[UploadFile]]) -> None:
    """Validate file counts, extensions, and content lengths."""
    if not files:
        return

    # Filter out empty form submissions
    valid_files = [f for f in files if f and f.filename]
    if len(valid_files) > settings.MAX_FILES:
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"Uploaded {len(valid_files)} files, which exceeds the limit of {settings.MAX_FILES} files per audit."
        )

    for f in valid_files:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in settings.SUPPORTED_FILE_EXTENSIONS:
            raise SecondOpinionException(
                ErrorCode.UNSUPPORTED_FILE_TYPE,
                f"File '{f.filename}' has unsupported extension '{ext}'. Supported extensions: {', '.join(settings.SUPPORTED_FILE_EXTENSIONS)}."
            )

def validate_source_presence(source_text: Optional[str], files: Optional[List[UploadFile]]) -> None:
    """Ensure at least one source input (pasted text or file) is provided."""
    has_text = bool(source_text and source_text.strip())
    has_files = bool(files and any(f and f.filename for f in files))

    if not has_text and not has_files:
        raise SecondOpinionException(
            ErrorCode.SOURCE_EMPTY_OR_UNREADABLE,
            "At least one source document or pasted reference text must be supplied."
        )

def validate_extracted_source_length(total_chars: int) -> None:
    """Ensure total extracted source text does not exceed safety cap."""
    if total_chars > settings.MAX_SOURCE_CHARS:
        raise SecondOpinionException(
            ErrorCode.CONTENT_TOO_LARGE,
            f"Total extracted source text ({total_chars} characters) exceeds the maximum allowed limit ({settings.MAX_SOURCE_CHARS})."
        )
