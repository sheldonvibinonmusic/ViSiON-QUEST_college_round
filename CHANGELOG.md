# Changelog

All completed project changes are documented in this file. Uncompleted or planned changes are never recorded as done.

## [0.6.0] - Phase 6 Documentation, Smoke Testing & Project Polish

### Added
- End-to-End CLI Smoke Test (`scripts/run_smoke_test.py`):
  - Validates full pipeline with multi-sentence input against synthetic policy text.
  - Verifies presence of `SUPPORTED_BY_SOURCE`, `CONTRADICTED_BY_SOURCE`, and `NOT_ESTABLISHED_BY_SOURCE`.
  - Confirms rules-only fallback and zero external API requirement.
- OpenAPI Schema Exporter (`scripts/export_openapi.py`):
  - Exports active FastAPI OpenAPI 3.1.0 schema to `contracts/openapi.json`.
- Model Checker Script (`scripts/check_model.py`):
  - Inspects local DeBERTa NLI model status and reports active verifier mode.
- Test Fixtures and Reference Examples (`examples/`):
  - `example_source.txt`: Reference remote work and equipment policy.
  - `example_answer.txt`: Representative AI answer with supported, contradicted, and unestablished claims.
  - `expected_findings.json`: Expected verdicts and rationale.
- Comprehensive Project Documentation (`README.md`):
  - Authoritative overview, tech stack, directory structure, setup commands, test evidence, and API specification.

## [0.5.0] - Phase 5 Frontend Forensic Dashboard & Audit Workspace

### Added
- Frontend Application Client (`frontend/src/api/client.ts`):
  - Strongly typed client for `/api/health`, `POST /api/audits`, and Markdown export.
  - Client-side JSON download helper (`downloadJsonReport`).
  - Client-side Markdown download helper (`downloadMarkdownReport`).
- Interactive Audit UI Components:
  - `AppHeader.tsx`: Responsive top navigation, ₹0 status badge, verifier mode indicator, and "New Audit" reset trigger.
  - `AuditForm.tsx`: Multi-input interface with character counter, "Paste Text" vs "Upload Files" tab switcher, and "Load Sample Policy Audit" 1-click test button.
  - `FileDropzone.tsx`: Drag-and-drop file upload component supporting PDF, DOCX, and TXT with file-count and size enforcement.
  - `AuditSummary.tsx`: Forensic executive summary card, transparent count badges for the 4 verdicts, safety warning callout, and one-click export actions (Copy Markdown, Download .md, Download JSON).
  - `OriginalAnswerViewer.tsx`: Renders the unmodified answer text with interactive span highlights matching claim findings; clicking any span selects the claim.
  - `ClaimList.tsx`: Claim cards displaying index, verdict badge, review priority, claim text quote, explanation, and advisory tags.
  - `EvidencePanel.tsx`: Sticky inspector displaying candidate source passages, exact quotes, page numbers, rank, character offsets, and relation indicators.
  - `VerdictBadge.tsx`: Reusable accessible badges with color coding and icons for the 4 verdicts and review priority levels.
- Span Segmentation Utility (`frontend/src/lib/offsets.ts`):
  - Splits unmodified answer string into text segments and highlighted claim spans without mutating character offsets.
- Frontend Unit Test Suite (`frontend/src/tests/`):
  - `offsets.test.ts`: Slicing and highlight segment preservation tests.
  - `verdict-labels.test.ts`: Verification of all 4 required verdict configurations.
  - Vitest test runner configured and passing (3/3 tests passed in 228ms).
- Production Build Verification:
  - Clean TypeScript check (`tsc -b`) and Vite production bundle generated in 597ms.
  - 100% backend test suite passing (23/23 tests in 1.48s).

## [0.4.0] - Phase 4 Audit Orchestration, API & Report Export

### Added
- Input Validation Service (`backend/app/services/validation.py`).
- Audit Pipeline Orchestrator (`backend/app/services/audit_service.py`).
- API Endpoints (`POST /api/audits`, `POST /api/audits/export/markdown`).
- Integration tests (`backend/tests/test_audit_api.py`).

## [0.3.0] - Phase 3 Retrieval, Rules Verifier & Verdict Mapping

### Added
- BM25 Evidence Retrieval Engine (`backend/app/services/retriever.py`) using `BM25Plus`.
- Deterministic Rules Engine (`backend/app/services/rules_verifier.py`).
- Safety Flags Service (`backend/app/services/safety_flags.py`).
- Lazy NLI Loader (`backend/app/services/nli_verifier.py`).
- Verdict Mapping Engine (`backend/app/services/verdict_mapper.py`).
- Summary Aggregation Service (`backend/app/services/summary_service.py`).

## [0.2.0] - Phase 2 Document Ingestion & Deterministic Segmentation

### Added
- Document parsing engine (`backend/app/services/document_parser.py`): TXT, PDF (`pypdf`), DOCX (`python-docx`).
- Source chunking (`backend/app/services/source_chunks.py`) and claim segmentation (`backend/app/services/claim_segmenter.py`).
- Test fixtures (`sample_policy.txt`, `sample_dates.txt`, `sample_mixed_answer.json`).

## [0.1.0] - Phase 1 Foundation

### Added
- Root configuration files: `.gitignore`, `.env.example`, `.python-version`, `pyproject.toml`, `IDEAS_FOR_APPROVAL.md`.
- Backend skeleton and health check `GET /api/health`.
- Node.js LTS v24.20.0 + React 19 + TypeScript + Vite 6 scaffold.
