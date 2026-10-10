"""
Input validation service for audit requests.
Validates character counts, file counts, sizes, extensions, and presence of required inputs.
"""
import os
import re
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

def validate_urls_metadata(urls: Optional[str]) -> List[str]:
    """
    Validate web URL input, deduplicate while preserving submission order,
    and enforce maximum URL count limit.
    """
    if not urls or not urls.strip():
        return []
    url_list = [u.strip() for u in re.split(r"[\n,]+", urls) if u.strip()]
    unique_urls = list(dict.fromkeys(url_list))
    if len(unique_urls) > settings.MAX_FILES:
        raise SecondOpinionException(
            ErrorCode.INVALID_INPUT,
            f"Provided {len(unique_urls)} URLs, which exceeds the limit of {settings.MAX_FILES} URLs per audit."
        )
    return unique_urls

def validate_source_presence(
    source_text: Optional[str],
    files: Optional[List[UploadFile]],
    urls: Optional[str] = None,
    allow_web_search: bool = False
) -> None:
    """Ensure at least one source input is provided, unless web search mode is enabled."""
    has_text = bool(source_text and source_text.strip())
    has_files = bool(files and any(f and f.filename for f in files))
    has_urls = bool(urls and urls.strip())

    if not has_text and not has_files and not has_urls and not allow_web_search:
        raise SecondOpinionException(
            ErrorCode.SOURCE_EMPTY_OR_UNREADABLE,
            "At least one source document, web URL, or pasted reference text must be supplied."
        )

def validate_extracted_source_length(total_chars: int) -> None:
    """Ensure total extracted source text does not exceed safety cap."""
    if total_chars > settings.MAX_SOURCE_CHARS:
        raise SecondOpinionException(
            ErrorCode.CONTENT_TOO_LARGE,
            f"Total extracted source text ({total_chars} characters) exceeds the maximum allowed limit ({settings.MAX_SOURCE_CHARS})."
        )
