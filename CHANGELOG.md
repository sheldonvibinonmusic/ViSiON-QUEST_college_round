# Changelog

## [0.10.0] - Deterministic Audit Engine Overhaul, Failure Map Resolution & Output Clarity

### Added
- **Deterministic Text & Number Normalizer** (`backend/app/services/normalizer.py`):
  - Added NFKC Unicode normalization, smart quote/dash cleanup, and tokenization.
  - Added full numeric/currency/multiplier equivalence parser equating `$45M` == `45 million` == `45,000,000`.
  - Added pure-Python suffix stemmer and zero-cost synonym/abbreviation expansions without external dependencies.
- **Fact-Slot Attribute Binding Engine** (`backend/app/services/fact_slots.py`):
  - Solves Failure Map F1 (Number Blindspot) by binding numerical quantities, metrics, and dates to nearest attribute nouns and named entities within tight lexical windows.
  - Compares numerical values only when attributes and entities match, eliminating false contradictions across different metrics and catching swapped financial numbers ($45M/$12M swap).
- **Modal Strength & Negation/Opposites Verifier** (`backend/app/services/modal_negation.py`):
  - Solves Failure Map F2 (Modal Inversion) and F5 (Negation and Opposites).
  - Classifies modal strength into obligations, prohibitions, permissions, and recommendations.
  - Detects modal shifts (e.g. should -> must) to downgrade to `AMBIGUOUS_OR_CONFLICTING` rather than falsely marking as supported.
  - Detects directional opposite clashes (increase vs decrease, more vs less, at least vs at most, allowed vs prohibited).
- **Exact-Entity & Citation Grounding Checker** (`backend/app/services/entity_checker.py`):
  - Solves Failure Map F3 (Hallucinated Citation Pass) by extracting statutory citations, RFC/ISO standards, case law citations, and proper nouns.
  - Blocks claims asserting ungrounded entities or fabricated citations from ever receiving `SUPPORTED_BY_SOURCE`.
- **Domain & Audience Scope Verifier** (`backend/app/services/scope_checker.py`):
  - Solves Failure Map F4 (Scope Swap) across claims, evidence, and governing section headings.
  - Detects conflicting scopes (commercial vs recreational, adult vs minor, public vs private, federal vs state/local).
- **Large Input Processing & Graceful Truncation** (`backend/app/services/audit_service.py`, `backend/app/services/document_parser.py`):
  - Solves Failure Map F7 by supporting large documents up to 50MB and safely handling inputs > 150k characters without crashing.
  - Caches and indexes the first 150k characters with `truncated=True` and clear explanatory telemetry.
  - Adds automatic detection for image-only scanned PDFs without digital text layers (`scanned_pdf_no_text`).
- **Bounded Same-Domain URL Subpage Crawling** (`backend/app/services/url_fetcher.py`):
  - Solves Failure Map F8 by discovering and crawling internal subpages on the same registered domain up to depth 2.
  - Strictly re-evaluates SSRF IP blocks, same-netloc constraints, and robots.txt policies for every subpage.
- **Per-Claim Exception Isolation & Deadline Management** (`backend/app/services/audit_service.py`, `backend/app/main.py`):
  - Solves Failure Map F9 by isolating evaluation errors on individual claims and returning well-formed partial findings if a deadline is reached.
  - Adds global exception handling to FastAPI for standardized error envelopes.
- **Output Clarity & Explainability** (`backend/app/schemas.py`, `frontend/src/components/EvidencePanel.tsx`, `frontend/src/components/ClaimList.tsx`, `frontend/src/components/AuditSummary.tsx`):
  - Solves Failure Map F10 by providing `verdict_reason` ("Why this verdict") and granular `checks` breakdown on every claim card and evidence inspector.
  - Adds calm UI notices for truncated inputs, explored subpages, and section numbers (§).
- **Comprehensive Failure Map Regression Test Suite** (`backend/tests/test_accuracy_engine.py`):
  - 12 comprehensive unit and integration tests verifying F1 through F10 with 100% pass rate.
- **Plain English Change Documentation** (`docs/CHANGES_EXPLAINED.md`):
  - 10-chapter simple English guide explaining each change, its root cause, and its proof like to a 10-year-old.

### Refactored
- `backend/app/services/rules_verifier.py`: Fully overhauled to synthesize signals from fact slots, modal negation, exact entities, and scope alignment.
- `backend/app/services/verdict_mapper.py`: Integrated conservative combiner logic with topic-specificity requirements to eliminate false contradictions.
- `frontend/src/components/FileDropzone.tsx`: Raised dropzone limit to 50MB with dynamic size indicators.


### Added
- **Four-Message Animated Rotating Headline** (`frontend/src/components/HeroContent.tsx`, `frontend/src/constants/headlines.ts`, `frontend/src/tests/headline.test.ts`):
  - Oversized cinematic rotating headline sequence cycling every ~4s with smooth enter (~700ms), stable hold (~2.4s), smooth exit (~700ms), and continuous loop.
  - Cycle sequence:
    1. "Where hallucinations come to an end."
    2. "Your AI fact-checking copilot."
    3. "Cross-check AI answers against PDFs, URLs, and source documents."
    4. "Find the claims supported by evidence—and the ones that aren't."
  - Fixed-height bounding box ensuring zero layout shift across desktop and mobile.
  - Screen-reader accessible with `aria-live="polite"` and `aria-atomic="true"`.
  - Immediate clickability maintained for "Open Auditor" and "Load Sample Policy" CTAs.
  - Vitest test suite (`frontend/src/tests/headline.test.ts`) asserting 4-message sequence and cycle wrap.
- **Cinematic Evidence Audit Space Journey** (`frontend/src/components/SpacecraftCraft.tsx`, `frontend/src/components/SpaceField.tsx`, `frontend/src/components/SceneOverlay.tsx`, `frontend/src/components/scene.css`):
  - Left-right desktop composition featuring a sleek forward-left exploration spacecraft with animated ion plasma thruster plumes and micro-drift orbital float.
  - Majestic planetary horizon arc rendered in Canvas 2D in the lower-left sector with dark obsidian mantle, deep atmospheric navy, rich orbital blue, and luminous cyan ozone halo.
  - Horizontal cosmic star velocity streaming and foreground streak trails matching forward-left spacecraft momentum.
  - Polished audit status panel on the right side with neutral stage labels ("Evidence Audit In Progress"), live ms ticker, animated word reveals, and 3-milestone progress rail.
  - Smooth 1200ms cubic bezier side-swap transition during Beat B.
  - Instant Skip button immediately jumping to ready results, and Cancel button cleanly retreating to workspace.

### Refactored
- **Open Auditor & Workspace Polish** (`frontend/src/components/AuditForm.tsx`, `frontend/src/components/AuditorWorkspace.tsx`):
  - Decongested form layout with clean 2-column header aligning title, description, and "Load Sample Policy" button.
  - Refined AI Answer textarea with character counter (`/ 40,000`), custom scrollbar, comfortable line height, and sky orbital focus ring.
  - Refined Source Material Tabs ("Paste Text", "Upload Files", "Web URLs") with icons and active indicators.
  - Refined action bar with primary "Run Evidence Audit" pill button, orbital glow, loading spinner, and keyboard shortcut pill (`Ctrl + Enter`).
  - Polished Auditor Workspace modal header with orbital shield badge and verifier mode pill.
  - Relative positioning enforced on `.hero` root container in `index.css` resolving desktop layering.


## [0.8.0] - Contract Synchronization, Verification Tooling & Telemetry Encodings

### Added
- Export OpenAPI CLI Telemetry (`scripts/export_openapi.py`):
  - Displays exported API route count and formatted schema file size in kilobytes.
- OpenAPI Contract Synchronization (`contracts/openapi.json`):
  - Regenerated contract specification reflecting `SourceFit`, `EvidenceOrigin`, and web evidence search response models.
- Smoke Test Performance Benchmark (`scripts/run_smoke_test.py`):
  - Measures sub-second audit pipeline execution latency and logs turnaround time.
- Span Coverage Telemetry (`backend/app/util/offsets.py`, `backend/tests/test_offsets.py`):
  - Added `calculate_char_coverage` utility to compute non-overlapping claim character coverage with full test suite.
- Source Fit UI Badge Configuration (`frontend/src/lib/labels.ts`, `frontend/src/tests/verdict-labels.test.ts`):
  - Added `SOURCE_FIT_CONFIG` styling definitions and Vitest assertion suite covering all 4 domain fitness states.
- Proposals Ledger Extension (`IDEAS_FOR_APPROVAL.md`):
  - Registered `IDEA-24` (Tabular CSV audit export) and `IDEA-25` (Sub-string whitespace discrepancies).

### Refactored
- `VerdictBadge.tsx`: Added `role="status"`, descriptive `aria-label` screen reader announcements, and JSDoc prop contracts.
- `citation_checker.py`: Hoisted `MIN_CITATION_OVERLAP_RATIO` constant with docstring explaining token predicate heuristics.
- `validation.py`: Enforced explicit `settings.MAX_URLS` limit in `validate_urls_metadata`.
- `README.md`: Consolidated test execution commands and updated accurate pass counts (100 backend + 6 frontend tests).

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
