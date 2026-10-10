# Changelog

All completed project changes are documented in this file. Uncompleted or planned changes are never recorded as done.

## [Unreleased] - Phase 2 Document Ingestion & Deterministic Segmentation

### Added
- Document parsing engine (`backend/app/services/document_parser.py`):
  - Canonical plain text extraction for TXT inputs.
  - Page-by-page digital text extraction from PDF via `pypdf` with 1-based page numbers.
  - Flowing text and table extraction from DOCX via `python-docx`.
  - SHA-256 document hashing and metadata tracking (`SourceDocument`).
  - Strict validation raising `SOURCE_EMPTY_OR_UNREADABLE` for empty or whitespace-only inputs.
- Paragraph-aware source chunking (`backend/app/services/source_chunks.py`):
  - Token-level slicing producing ~120-220 word chunks with ~40 word overlap.
  - Exact character offsets (`[start_char:end_char]`) into the extracted document text.
  - Page provenance mapping associating each chunk with its 1-based document page number.
- Deterministic claim segmentation (`backend/app/services/claim_segmenter.py`):
  - Punctuation-based sentence splitting with abbreviation protection (e.g. `Dr.`, `Prof.`, `e.g.`, `vs.`).
  - Decimal number protection (e.g. `4.5%`, `3.14`).
  - Closing quote boundary handling (`."`, `!"`, `?"`).
  - Zero-based, end-exclusive Unicode code-point offsets into the unmodified answer string.
  - Verified invariant: `answer[claim.start_char:claim.end_char] == claim.text` for 100% of claims.
- Offset and hashing utilities (`backend/app/util/offsets.py`, `backend/app/util/hashes.py`).
- Synthetic fixtures (`sample_policy.txt`, `sample_dates.txt`, `sample_mixed_answer.json`).
- Automated test suites:
  - `backend/tests/test_parsers.py`: TXT, PDF, DOCX, and chunking offset validation.
  - `backend/tests/test_offsets.py`: Sentence splitting, abbreviation guards, and offset match validation.
  - All 13 backend tests passing (100% pass rate).

## [0.1.0] - Phase 1 Foundation

### Added
- Root configuration files: `.gitignore`, `.env.example`, `.python-version`, `pyproject.toml`, `IDEAS_FOR_APPROVAL.md`.
- Python backend packages installed in `.venv`: `fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, `rank-bm25`, `pypdf`, `python-docx`, `numpy`.
- Backend application structure:
  - `backend/app/config.py`: Environment configuration and safety limits.
  - `backend/app/errors.py`: Standardized error and warning codes.
  - `backend/app/schemas.py`: Pydantic v2 data models for health check and audit pipeline contracts.
  - `backend/app/api/audit_routes.py`: Health check route `GET /api/health`.
  - `backend/app/main.py`: FastAPI application entry point with CORS.
  - `backend/tests/test_health.py`: Health endpoint integration tests (100% pass).
- Frontend toolchain and application:
  - Node.js LTS v24.20.0 and npm 11.19.0 installed and verified.
  - React 19 + TypeScript + Vite 6 scaffolded in `frontend/`.
  - Tailwind CSS + Lucide icons installed and configured.
  - Vite proxy configured for `/api` to local FastAPI backend.
  - `frontend/src/App.tsx`: Initial responsive forensic dashboard layout and live health-check consumer.
  - Frontend production build verified with `npm run build`.
