# Changelog

## Phase 3(d) — Space journey and side swaps
- Added one full-screen, low-detail Canvas 2D star layer and a CSS focal cluster that glides opposite the thinking panel.
- Connected the existing scene overlay to the mirrored scene-state events so the A/B/C layout follows `getStageEvents()` while actual backend activity text remains event-sourced.
- Added the approved silver text sweep, word cross-fades, estimated-beat rail, elapsed-millisecond ticker, and abstract drifting evidence marks.
- Kept the existing doorway transition, Run flow, workspace modal, and results lifecycle; planet, asteroid, and black-hole visuals remain for Phase 3(e).

## Phase 3(c) — Door opening transition
- Added an isolated, full-screen doorway overlay with a 700 ms CSS camera push, growing light slit, and one smooth white flash; the existing video and poster assets remain untouched.
- Measured the video doorway center from a decoded 1664×1248 frame at 2.51 s and accounted for the existing poster fallback's separate center.
- Added keyboard-accessible Skip and Cancel animation controls; reduced-motion and mobile modes omit the push and flash.

All completed project changes are documented in this file. Uncompleted or planned changes are never recorded as done.

## [0.7.0] - UI Implementation, Hostile Hardening, Pipeline Stress Testing & Error Fixing

### Added
- Phase 1 UI Capabilities (`UI_HANDOFF_NEEDS.md` implementation):
  - Added "Web URLs" 3rd tab in `AuditForm.tsx` with validation, chip list, and duplicate prevention.
  - Added free Web Search Fallback toggle in `AuditForm.tsx`.
  - Added Source Fit badge and prominent Domain Mismatch amber banner in `AuditSummary.tsx`.
  - Added Incomplete Audit status badge and advisory banner in `AuditSummary.tsx`.
  - Added Evidence Origin badges (`User File`, `Web URL`, `Wikipedia`, `arXiv`, `Crossref`, `Web Search`), external links, and Citation Verified chips in `EvidencePanel.tsx`.
  - Added Independent Sources Agreeing corroboration counter chip in `ClaimList.tsx`.
  - Added Web Evidence search queries budget usage strip in `AuditSummary.tsx`.
- Phase 2 Hostile Server Attack Test Suite (`backend/tests/test_hostile_server.py`):
  - In-process Starlette ASGI hostile server testing SSRF defense: credentialed URLs, non-HTTP schemes, IPv6 and IPv4-mapped loopbacks, cloud instance metadata IP (`169.254.169.254`), redirect loops, binary media types, chunk-by-chunk stream byte caps (>2MB), gzip bombs, polite `robots.txt` enforcement, mixed encodings, hidden text tag discarding, and prompt injection evidence isolation.
- Phase 2 Real Public URLs Test Suite (`backend/tests/test_real_urls.py`):
  - 13 live web categories marked with `@pytest.mark.integration`: Encyclopedia, arXiv abstract, PDF rejection, news article, React SPA/JS-heavy, Python documentation, French Wikipedia, HTTP 404, login page, image URL rejection, URL shortener redirect, W3C specification, and tracking parameters.
- Phase 2 Pipeline Stress Test Suite (`backend/tests/test_pipeline_stress.py`):
  - 15 pipeline stress cases: physics answer with maths source, maths answer with physics source, relevant source, partly relevant source, contradicting source, no source (web mode), mixed mode, two sources with one off-topic, single provider failure fallback, all providers failing graceful warning, malformed/empty URL list, URL cap rejection (>5 URLs), duplicate URL deduplication, concurrent requests (`asyncio.gather`), and partway audit timeout with `status="incomplete"`.
- Error Log Ledger (`ERROR_LOG.md`):
  - Tracks 9 vulnerabilities and bug fixes (ERR-001 through ERR-009) with root causes, fixes, and regression test proofs.

### Fixed
- Fixed embedded credential leak vulnerability in URL parser (`ERR-001`).
- Fixed hidden CSS/attribute text extraction vulnerability in `HTMLContentExtractor` (`ERR-002`).
- Fixed unbounded memory consumption and gzip bomb susceptibility with early streaming caps (`ERR-003`).
- Fixed scraper politeness by verifying `robots.txt` disallow policies (`ERR-004`).
- Fixed unvalidated URL submission count by enforcing 5-URL cap in `validation.py` (`ERR-005`).
- Fixed audit timeouts to return graceful `status="incomplete"` with partial findings (`ERR-006`).
- Fixed `UnboundLocalError` on `is_incomplete` during domain mismatch audits (`ERR-007`).
- Fixed `MagicMock` type check and async close compatibility in test runners (`ERR-008`).
- Fixed provider chain crashes on external provider network failures with isolated try/except blocks (`ERR-009`).

## [Unreleased]

### Added
- Ctrl+Enter (Windows/Linux) and ⌘+Enter (macOS) submit the existing audit form through its current validation and Run flow.

### Fixed
- Restored the missing verdict-label and answer-offset utilities, and scoped Python `lib` ignore rules to the repository root so the frontend modules are not ignored.
- Converted backend Unicode code-point offsets to JavaScript UTF-16 indexes before highlighting claims.

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
