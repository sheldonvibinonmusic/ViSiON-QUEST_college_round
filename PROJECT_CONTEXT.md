# Second Opinion — Evidence-Grounded AI Answer Auditor

> **Document status:** IMPLEMENTED as a README artifact in the current working environment; the application repository itself does not yet exist. The content below records confirmed requirements separately from proposed implementation details. [Evidence: “no repository yet” and “Start with a clean project structure” | where in chat: late, Stage 2 answers 1 and 8]
>
> **Evidence policy:** Every project claim in this document is accompanied by an evidence tag pointing to the chat, a user answer, or an earlier planning artifact. A proposal is not evidence that code exists. [Evidence: “Never present a PROPOSED item as decided” | where in chat: late, README master prompt, Golden Rules]
>
> **Current implementation status:** No application code has been reported as implemented or tested. [Evidence: “Not tested yet” and “Treat the frontend, backend, model integrations, document processing, retrieval, evaluation and deployment as planned capabilities” | where in chat: late, Stage 2 answer 9]

## Status vocabulary

The project ledger uses the four statuses required by the user. [Evidence: “Label every feature or file with exactly one status” | where in chat: late, README master prompt, Status Rule]

- **IMPLEMENTED** — an artifact or action is confirmed to exist in the chat or available working environment; this does not imply that the application works. [Evidence: “IMPLEMENTED (code or confirmation exists in chat)” | where in chat: late, README master prompt, Status Rule]
- **DECIDED** — a requirement or direction was explicitly confirmed, but may not yet be built. [Evidence: “DECIDED (agreed, not built yet)” | where in chat: late, README master prompt, Status Rule]
- **PROPOSED** — a technology, path, or implementation idea was suggested but was not confirmed as implemented or final. [Evidence: “PROPOSED (suggested, never agreed)” | where in chat: late, README master prompt, Status Rule]
- **DROPPED** — an item was explicitly abandoned. [Evidence: “DROPPED (explicitly abandoned)” | where in chat: late, README master prompt, Status Rule]

An item labelled “INFERRED, needs confirmation” is kept outside the main tree, as requested, and also carries one of the four statuses above. [Evidence: “Mark any file you inferred as ‘INFERRED, needs confirmation’ and keep it out of the main tree” | where in chat: late, README master prompt, Stage 3]

---

## 1. Project Name and One-Line Pitch

**Project name:** Second Opinion. **Status: DECIDED.** [Evidence: “Second Opinion — Evidence-Grounded AI Answer Auditor” | where in chat: late, architecture master prompt, §2]

**One-line pitch:** An evidence-grounded AI-answer auditor that compares a submitted answer against user-provided source documents, highlights claims requiring review, and shows the passages that support or contradict the assessment. **Status: DECIDED.** [Evidence: “evaluates AI-generated answers against provided source material” and “display the relevant evidence” | where in chat: late, architecture master prompt, §2]

**Initial audience:** Students and researchers verifying AI-generated answers against textbooks, papers, reports, or reference PDFs; developers are the secondary audience. **Status: DECIDED.** [Evidence: “Students and researchers … with developers as a secondary audience” | where in chat: late, Stage 2 answer 7]

**Repository state:** There is no GitHub repository yet and no implementation folder or README was supplied for inspection. **Status: IMPLEMENTED as a recorded project-state fact.** [Evidence: “no repository yet,” “None available” | where in chat: late, Stage 2 answers 1 and 8]

## 2. Problem Statement

AI-generated answers can sound convincing while containing fabricated facts, unsupported claims, contradictions, or flawed reasoning. **Status: DECIDED.** [Evidence: “AI-generated answers can sound convincing even when they contain fabricated facts, unsupported claims or flawed reasoning” | where in chat: late, architecture master prompt, §2]

Second Opinion is intended to evaluate an answer against supplied evidence and show what the system found, why it found it, and which source passage was used. **Status: DECIDED.** [Evidence: “Users should be able to see exactly what is wrong, why it is wrong, which source supports the assessment” | where in chat: late, architecture master prompt, §2]

The project must not automatically treat a claim missing from the supplied documents as false. **Status: DECIDED.** [Evidence: “It must not automatically label an unsupported claim as false” | where in chat: late, architecture master prompt, §2]

Factual support, contradiction, insufficient evidence, logical validity, ambiguity, and safety concerns are different assessment dimensions. **Status: DECIDED.** [Evidence: “Safety, factuality and logical consistency are related but separate evaluation dimensions” | where in chat: late, architecture master prompt, §3]

The project is an auditing aid and must not be presented as a certified medical, legal, or financial decision-making system. **Status: DECIDED.** [Evidence: “Do not position the initial prototype as a certified medical, legal or financial decision-making system” | where in chat: late, Stage 2 answer 7]

## 3. Objective and Success Criteria

### 3.1 Objective

The core objective is to accept an AI-generated answer and source text or documents, audit the answer against those sources, and return evidence-linked findings. **Status: DECIDED.** [Evidence: “submit an answer, upload reference documents, run an audit, inspect the findings and export the audit report” | where in chat: late, Stage 2 answer 4]

The core audit must operate without a paid API or externally hosted language model. **Status: DECIDED.** [Evidence: “The core source-grounded auditing workflow must work without a paid API or externally hosted LLM” | where in chat: late, Stage 2 answer 5]

The primary result must preserve the difference between `SUPPORTED_BY_SOURCE`, `CONTRADICTED_BY_SOURCE`, `NOT_ESTABLISHED_BY_SOURCE`, and `AMBIGUOUS_OR_CONFLICTING`. These exact names are from the proposed architecture contract, while the need to keep those outcomes distinct is user-confirmed. **Status: DECIDED for the distinction; PROPOSED for the exact enum spellings.** [Evidence: “Preserve distinct outcomes for supported, contradicted, insufficient-evidence and ambiguous claims” | where in chat: late, Stage 2 answer 5; exact enum names in architecture blueprint, “ClaimFinding”]

The app must offer a way to download or save the audit report. **Status: DECIDED.** [Evidence: “Provide a way to download or save the audit report” | where in chat: late, Stage 2 answer 4]

### 3.2 Success criteria recorded in the chat

The following are required behaviours; they are not evidence that the behaviours have been implemented. [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

| Criterion | Status | Evidence |
|---|---|---|
| Accept a non-empty AI-generated answer and reference source text and/or supported files. | DECIDED | [Evidence: “paste an answer, upload reference documents” | where in chat: late, Stage 2 answer 4] |
| Return claim-level findings linked to source evidence or explicitly indicate that no useful passage was found. | DECIDED | [Evidence: “each finding … relevant evidence” and “An explicit indication when evidence is insufficient” | where in chat: late, architecture master prompt, §6] |
| Preserve original answer text and highlight relevant spans. | DECIDED | [Evidence: “Preserve the original answer” and “original-text highlighting” | where in chat: late, architecture master prompt, §§6–7] |
| Keep source-supported claims distinct from contradicted and not-established claims. | DECIDED | [Evidence: “do not automatically call it false” | where in chat: late, architecture master prompt, §2] |
| Provide a transparent summary that does not hide an individual severe issue in a single percentage. | DECIDED | [Evidence: “An overall assessment that does not conceal severe individual errors” | where in chat: late, architecture master prompt, §2] |
| Export or save the audit output. | DECIDED | [Evidence: “export the audit report” | where in chat: late, Stage 2 answer 4] |
| Run without a required external API key. | DECIDED | [Evidence: “the application must not become unusable when an API key is absent” | where in chat: late, Stage 2 answer 5] |
| Work reliably as a local demonstration before optional public deployment. | DECIDED | [Evidence: “Develop and validate the complete application locally first” | where in chat: late, Stage 2 answer 6] |
| Pass an end-to-end test and a small labelled test set before performance claims are made. | DECIDED | [Evidence: “Do not report implementation progress, working features or performance results until they have been demonstrated through actual execution and testing” | where in chat: late, Stage 2 answer 9] |

**Measured success thresholds:** NOT SPECIFIED IN CHAT. [Evidence: the prompt requires appropriate metrics but says not to invent performance targets | where in chat: late, architecture master prompt, §10]

## 4. Target Users

### Primary users

Students and researchers who generate answers with an AI assistant and compare them against a textbook, paper, report, or reference PDF. **Status: DECIDED.** [Evidence: “The initial use case is straightforward: a student or researcher generates an answer … provides the relevant textbook, paper, report or reference PDF” | where in chat: late, Stage 2 answer 7]

### Secondary users

Developers who want to inspect source-grounded AI answers. **Status: DECIDED.** [Evidence: “with developers as a secondary audience” | where in chat: late, Stage 2 answer 7]

### Target groups not confirmed

Enterprise compliance teams, medical professionals, legal professionals, financial advisers, journalists, and other specialist customer segments: **NOT SPECIFIED IN CHAT** as initial target users. [Evidence: the user specified students/researchers and developers as the initial audiences | where in chat: late, Stage 2 answer 7]

## 5. Scope (In / Out / Deferred)

### 5.1 In scope for the initial MVP

| Item | Status | Evidence |
|---|---|---|
| Paste an AI-generated answer. | DECIDED | [Evidence: “submit an answer” | where in chat: late, Stage 2 answer 4] |
| Paste reference text and/or upload PDF, TXT, or DOCX source documents. | DECIDED | [Evidence: “pypdf + python-docx + TXT support” | where in chat: late, Stage 2 answer 3] |
| Extract readable document text and preserve available source identity/page metadata. | DECIDED | [Evidence: “preserves document identity and useful page or section metadata” | where in chat: late, architecture master prompt, §6] |
| Deterministic sentence/paragraph splitting with source offsets. | DECIDED | [Evidence: “Deterministic sentence/paragraph chunking with source offsets” | where in chat: late, Stage 2 answer 3] |
| Retrieve candidate evidence locally with BM25. | DECIDED | [Evidence: “Retrieval: BM25” | where in chat: late, Stage 2 answer 3] |
| Use local DeBERTa NLI as an optional assessment signal. | DECIDED | [Evidence: “Local DeBERTa NLI as an optional assessment signal” | where in chat: late, Stage 2 answer 3] |
| Keep NLI separate from an independent authority on truth. | DECIDED | [Evidence: “Treat DeBERTa NLI as an evidence-assessment component, not as an independent authority on truth” | where in chat: late, Stage 2 answer 5] |
| Return distinct supported, contradicted, insufficient-evidence, and ambiguous results. | DECIDED | [Evidence: “Preserve distinct outcomes for supported, contradicted, insufficient-evidence and ambiguous claims” | where in chat: late, Stage 2 answer 5] |
| Show original answer, relevant findings, and source evidence. | DECIDED | [Evidence: “inspect the original answer, select a flagged passage, read the relevant source evidence” | where in chat: late, Stage 2 answer 7] |
| Export or save the audit report. | DECIDED | [Evidence: “Provide a way to download or save the audit report” | where in chat: late, Stage 2 answer 4] |
| Keep the MVP local-first and transient. | DECIDED | [Evidence: “Keep the initial MVP transient and local-first” | where in chat: late, Stage 2 answer 4] |
| Avoid a database, authentication, and persistent server-side audit history in the first implementation. | DECIDED | [Evidence: “Do not introduce a database, authentication system or persistent server-side audit history during the first implementation” | where in chat: late, Stage 2 answer 4] |

### 5.2 Deferred or optional

| Item | Status | Evidence |
|---|---|---|
| External-web verification. | PROPOSED | [Evidence: “External-source verification may be supported as a separate optional mode” | where in chat: late, architecture master prompt, §6] |
| Hosted LLM providers. | PROPOSED | [Evidence: “Hosted models may be considered optional enhancements” | where in chat: late, Stage 2 answer 5] |
| LettuceDetect span-level model. | PROPOSED | [Evidence: “P2 optional enhancement after NLI and dashboard pass tests” | where in chat: middle, architecture blueprint, model comparison] |
| Embeddings-based retrieval. | PROPOSED | [Evidence: “Embedding-based retrieval if BM25 misses paraphrased evidence in the evaluation set” | where in chat: middle, architecture blueprint, P2 scope] |
| Multilingual claim segmentation and multilingual NLI. | PROPOSED | [Evidence: “Multilingual claim segmentation and multilingual NLI” | where in chat: middle, architecture blueprint, P2 scope] |
| OCR for scanned PDFs. | PROPOSED | [Evidence: “Scanned PDF OCR” is listed as future/stret ch work | where in chat: middle, architecture blueprint, P2 scope] |
| SQLite history. | DROPPED for initial MVP; may be reconsidered later. | [Evidence: “Do not introduce a database … during the first implementation” | where in chat: late, Stage 2 answer 4; earlier optional SQLite plan in architecture blueprint is superseded] |
| Authentication and multi-user history. | DROPPED for initial MVP; may be reconsidered later. | [Evidence: “Do not introduce … authentication system or persistent server-side audit history” | where in chat: late, Stage 2 answer 4] |
| Model training from scratch. | DROPPED from the hackathon scope. | [Evidence: “Do not attempt to train a large model from scratch during the hackathon” | where in chat: late, architecture master prompt, §10] |
| Full formal proof of arbitrary natural-language reasoning. | DROPPED from the initial MVP. | [Evidence: “Do not claim full formal proof … unless a defined formalisation and verification process can substantiate that claim” | where in chat: late, architecture master prompt, §6] |
| Paid APIs as required runtime dependencies. | DROPPED. | [Evidence: “The core source-grounded auditing workflow must work without a paid API” | where in chat: late, Stage 2 answer 5] |
| A vector database in the initial MVP. | DROPPED. | [Evidence: “A vector database before retrieval need is demonstrated” is explicitly out of scope | where in chat: middle, architecture blueprint, out-of-scope list] |

## 6. Complete Tech Stack

The following stack reflects your latest confirmation. It is a **DECIDED starting direction**, not an assertion that dependencies are installed or that the stack can no longer be changed. You explicitly said “we will improve if needed.” [Evidence: “yes we will improve if needed” followed by the stack list | where in chat: late, Stage 2 answer 3]

| Item | Role in project | Why selected in the chat | Status and evidence |
|---|---|---|---|
| React | Frontend user interface. | Named in the user-confirmed frontend stack. | DECIDED [Evidence: “Frontend: React + TypeScript + Vite” | where in chat: late, Stage 2 answer 3] |
| TypeScript | Frontend language/type checking. | Named in the user-confirmed frontend stack. | DECIDED [Evidence: “Frontend: React + TypeScript + Vite” | where in chat: late, Stage 2 answer 3] |
| Vite | Frontend toolchain/dev server/build tool. | Named in the user-confirmed frontend stack. | DECIDED [Evidence: “Frontend: React + TypeScript + Vite” | where in chat: late, Stage 2 answer 3] |
| Python | Backend language. | Named in the user-confirmed backend stack. | DECIDED [Evidence: “Backend: Python + FastAPI” | where in chat: late, Stage 2 answer 3] |
| FastAPI | Backend HTTP API framework. | Named in the user-confirmed backend stack and earlier architecture. | DECIDED [Evidence: “Backend: Python + FastAPI” | where in chat: late, Stage 2 answer 3] |
| Local DeBERTa NLI | Optional assessment signal that compares claims with retrieved evidence. | Chosen as the starting local assessment model, but not as a truth oracle. | DECIDED [Evidence: “Local DeBERTa NLI as an optional assessment signal” | where in chat: late, Stage 2 answer 3] |
| `microsoft/deberta-base-mnli` | Exact proposed DeBERTa NLI model identifier. | Named by the architecture blueprint for source-premise/claim-hypothesis inference. | PROPOSED [Evidence: “Primary local verifier: `microsoft/deberta-base-mnli`” | where in chat: middle, architecture blueprint] |
| BM25 | Local evidence retrieval. | Selected in your user-confirmed stack. | DECIDED [Evidence: “Retrieval: BM25” | where in chat: late, Stage 2 answer 3] |
| `rank-bm25` | Proposed Python BM25 implementation. | Named in the cost audit as the simple local retrieval dependency. | PROPOSED [Evidence: “Evidence retrieval — `rank-bm25`” | where in chat: late, cost audit] |
| Deterministic sentence/paragraph splitting | Split text while keeping source offsets. | Confirmed by you as the text-splitting approach. | DECIDED [Evidence: “Deterministic sentence/paragraph chunking with source offsets” | where in chat: late, Stage 2 answer 3] |
| `pypdf` | PDF text extraction library in the confirmed starting direction; actual installation is not confirmed. | Named by you in the Stage 2 stack answer and previously in the cost audit. | DECIDED as starting direction [Evidence: “Documents: pypdf + python-docx + TXT support” | where in chat: late, Stage 2 answer 3] |
| `python-docx` | DOCX text extraction library in the confirmed starting direction; actual installation is not confirmed. | Named by you in the Stage 2 stack answer and previously in the cost audit. | DECIDED as starting direction [Evidence: “Documents: pypdf + python-docx + TXT support” | where in chat: late, Stage 2 answer 3] |
| TXT support | Plain-text source input/extraction. | Confirmed by you as part of the selected stack. | DECIDED [Evidence: “pypdf + python-docx + TXT support” | where in chat: late, Stage 2 answer 3] |
| SQLite | Optional later database/history extension. | Explicitly excluded from the initial MVP. | DROPPED for initial MVP [Evidence: “Do not introduce a database” | where in chat: late, Stage 2 answer 4] |
| PostgreSQL | Database candidate discussed in the architecture prompt. | No database is needed for the initial transient MVP. | DROPPED for initial MVP [Evidence: “Do not introduce a database” | where in chat: late, Stage 2 answer 4] |
| Tailwind CSS | Proposed frontend styling system. | Suggested in the architecture research and cost audit; not yet confirmed by you. | PROPOSED [Evidence: “Tailwind CSS + a small subset of shadcn/ui/Radix + Lucide” | where in chat: late, cost audit] |
| shadcn/ui | Proposed React UI component system. | Suggested as a small, selective component set. | PROPOSED [Evidence: “shadcn/ui” | where in chat: middle, architecture master prompt, §5F] |
| Radix UI | Proposed accessible UI primitives. | Listed as a candidate for accessible UI components. | PROPOSED [Evidence: “Radix UI primitives or equivalent” | where in chat: middle, architecture master prompt, §5F] |
| Lucide icons | Proposed icon library. | Listed in the candidate UI stack. | PROPOSED [Evidence: “Lucide icons” | where in chat: middle, architecture master prompt, §5F] |
| Uvicorn | Proposed ASGI server for FastAPI. | Named in the architecture blueprint’s primary stack. | PROPOSED [Evidence: “FastAPI + Uvicorn + Pydantic v2” | where in chat: middle, architecture blueprint] |
| Pydantic | Proposed backend data validation and API schemas. | The blueprint proposes Pydantic models as the backend’s authoritative contract. | PROPOSED [Evidence: “Pydantic models are canonical on the backend” | where in chat: middle, architecture blueprint] |
| pytest | Proposed backend test runner. | Named in the architecture blueprint. | PROPOSED [Evidence: “pytest + FastAPI TestClient/httpx” | where in chat: middle, architecture blueprint] |
| Vitest | Optional frontend test runner. | The architecture says frontend tests may be added if time allows. | PROPOSED [Evidence: “small frontend tests with Vitest if time allows” | where in chat: middle, architecture blueprint] |
| Git | Version control. | Required by the stated code-push cadence. | DECIDED [Evidence: “push the code every three hours” | where in chat: early, initial hackathon request] |
| GitHub | Potential remote repository host. | GitHub Free was recommended, but you confirmed no repository yet. | PROPOSED [Evidence: “Git + GitHub Free” in cost audit; “no repository yet” in Stage 2 answer 1 | where in chat: late] |
| Antigravity | AI-assisted development environment/tool. | Named by you as one of the coding agents/tools. | DECIDED as a development tool [Evidence: “hand it to coding agents” and “Antigravity” | where in chat: late, architecture master prompt and earliest request] |
| Google AI Studio (development tool) | AI-assisted development/tooling. | Named by you as a coding tool; this does not confirm its use as an application runtime provider. | DECIDED [Evidence: “using by coding and using AI … anti-gravity and Google AI Studio” | where in chat: early, initial request] |
| Google AI Studio / Gemini API (optional runtime provider) | Optional hosted inference experiment, not required for core auditing. | Mentioned as an API provider candidate; later user confirmed the core audit must work without hosted inference. | PROPOSED [Evidence: “Possible services to examine include Google AI Studio/Gemini API” and “Hosted models may be considered optional enhancements” | where in chat: middle, architecture master prompt, §5B; late, Stage 2 answer 5] |
| Docker | Optional containerisation/deployment route. | Discussed as a possible route, but free deployment is not guaranteed. | PROPOSED [Evidence: “`Dockerfile` — optional public deployment” | where in chat: middle, architecture blueprint] |

### Runtime versions

The architecture blueprint proposed Python 3.11.x and Node 22.x LTS as baselines. These versions were not confirmed through an actual project install. **Status: PROPOSED.** [Evidence: “Use Python 3.11.x” and “Node 22.x LTS” | where in chat: middle, architecture blueprint, runtime/version policy]

The exact package versions and lockfiles are **NOT SPECIFIED IN CHAT** as installed project dependencies. [Evidence: the blueprint says actual lockfiles should be created during scaffold/install | where in chat: middle, architecture blueprint, runtime/version policy]

## 7. System Architecture

### 7.1 Intended data flow

The architecture blueprint proposed this sequence: user input → document ingestion → text extraction → source preparation → claim identification → evidence retrieval → claim evaluation → finding aggregation → response rendering. The user has since confirmed that the MVP is transient and local-first. **Status: PROPOSED implementation flow with DECIDED local-first/transient constraint.** [Evidence: architecture sequence in architecture master prompt, §7; “Keep the initial MVP transient and local-first” | where in chat: late, Stage 2 answer 4]

```text
User supplies answer + source text/files
             |
             v
       Frontend form
             |
             v
      FastAPI audit endpoint
             |
             v
 Validate inputs and file limits
             |
             v
 Extract text from TXT / PDF / DOCX
             |
             v
 Prepare source chunks + offsets
             |
             v
 Split answer into claim-sized spans
             |
             v
 BM25 retrieves candidate source passages
             |
             v
 Local DeBERTa NLI assessment (optional signal)
             |
             v
 Rules / verdict mapping / warnings
             |
             v
 Audit findings + evidence + summary
             |
             v
 Dashboard, highlighting, report export
```

**Status:** PROPOSED. The diagram is a transcription of the discussed architecture, not an implemented runtime trace. [Evidence: “user input → document ingestion → text extraction → source preparation → claim identification → evidence retrieval → claim evaluation → finding aggregation” | where in chat: middle, architecture master prompt, §7]

### 7.2 Component responsibilities

- **Frontend:** Collect the answer and source inputs, display analysis state, render results and evidence, highlight findings, and offer export. **Status: DECIDED for these product behaviours; PROPOSED for exact component implementation.** [Evidence: “submit an answer … inspect the findings and export the audit report” | where in chat: late, Stage 2 answer 4]
- **FastAPI backend:** Accept the audit request, validate inputs, call extraction/retrieval/assessment functions, and return structured findings. **Status: PROPOSED.** [Evidence: the architecture blueprint’s `POST /api/audits` design | where in chat: middle, architecture blueprint]
- **Document parser:** Extract text from PDF, TXT, and DOCX inputs and retain source identity/page information when it is available. **Status: DECIDED for input formats; PROPOSED for parser code.** [Evidence: Stage 2 answer 3; architecture master prompt, §6]
- **Claim segmentation:** Divide the answer into auditable units while preserving original-text offsets. **Status: DECIDED.** [Evidence: “Deterministic sentence/paragraph chunking with source offsets” | where in chat: late, Stage 2 answer 3]
- **Retriever:** Select candidate source passages via BM25; retrieval rank does not itself establish factual support. **Status: DECIDED for BM25; PROPOSED for implementation.** [Evidence: “Retrieval: BM25” | where in chat: late, Stage 2 answer 3; “Low lexical rank is a retrieval weakness, not a truth verdict” | architecture blueprint]
- **NLI assessment:** Compare a claim against candidate evidence, treating the model as a signal rather than a truth authority. **Status: DECIDED.** [Evidence: “Treat DeBERTa NLI as an evidence-assessment component, not as an independent authority on truth” | where in chat: late, Stage 2 answer 5]
- **Verdict mapper:** Convert model/rule/retrieval signals to the separate evidence verdicts. **Status: PROPOSED.** [Evidence: “Use `verdict` values” and the four evidence outcomes | where in chat: middle, architecture blueprint]
- **Transient result handling:** Keep active audit results in application/session memory without server-side persistent history. **Status: DECIDED.** [Evidence: “Results may remain in application memory for the active session, but server-side persistence is unnecessary” | where in chat: late, Stage 2 answer 4]
- **Report export:** Provide a downloadable or savable output. **Status: DECIDED for the capability; PROPOSED for the format/implementation.** [Evidence: “Provide a way to download or save the audit report” | where in chat: late, Stage 2 answer 4]

### 7.3 Failure behaviour

The architecture proposes clear error responses for empty answers, unreadable or empty sources, oversized inputs, unsupported file types, and failed audits. **Status: PROPOSED.** [Evidence: listed validation error codes in architecture blueprint, `POST /api/audits` contract]

If the local NLI model cannot load or its label mapping cannot be validated, the proposed system switches to rules-only mode and displays a warning; it must not imply that NLI-backed verification ran successfully. **Status: PROPOSED.** [Evidence: “switch to `rules_only`” and “`MODEL_FALLBACK_RULES_ONLY` warning” | where in chat: middle, architecture blueprint]

If no usable source evidence is found, the proposed result is insufficient/not established rather than contradicted. **Status: DECIDED as a product rule.** [Evidence: “It must not automatically label an unsupported claim as false” | where in chat: late, architecture master prompt, §2]

## 8. Full File and Folder Structure

### 8.1 Status of this tree

The tree below is the proposed tree from the architecture blueprint. **All application paths shown are PROPOSED, not IMPLEMENTED.** [Evidence: “no repository yet” and “None available” | where in chat: late, Stage 2 answers 1 and 8]

The blueprint deliberately did not include `README.md` because the README was deferred at that stage. Your later request supersedes that deferral and this document supplies README content, but the exact repository-relative placement was not confirmed by a literal path in the original tree. **Status: DECIDED for the README requirement; INFERRED, needs confirmation for `second-opinion/README.md`.** [Evidence: “Do not generate `README.md` yet” in earlier architecture prompt; later “Produce one very large, detailed README.md” | where in chat: middle and late messages]

```text
second-opinion/                         [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── .gitignore                          [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── .env.example                        [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── .python-version                     [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── pyproject.toml                      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── uv.lock                             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── package.json                        [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── package-lock.json                   [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── Dockerfile                          [PROPOSED — optional] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── contracts/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   └── api-notes.md                    [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── docs/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── ARCHITECTURE.md                 [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── DATA_CONTRACTS.md               [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── TEST_PLAN.md                    [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   └── DEPLOYMENT.md                   [PROPOSED — optional] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── backend/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── app/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── __init__.py                 [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── main.py                     [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── config.py                   [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── errors.py                   [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── schemas.py                  [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── api/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── __init__.py             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   └── audit_routes.py         [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   ├── services/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── __init__.py             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── audit_service.py        [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── validation.py           [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── document_parser.py      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── source_chunks.py        [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── claim_segmenter.py      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── retriever.py             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── nli_verifier.py         [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── rules_verifier.py       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── verdict_mapper.py       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   ├── safety_flags.py         [PROPOSED — optional] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   │   └── summary_service.py      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │   └── util/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │       ├── __init__.py             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │       ├── hashes.py               [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   │       └── offsets.py              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   └── tests/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── test_health.py              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── test_parsers.py             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── test_offsets.py             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── test_retriever.py           [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── test_verdict_mapper.py      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── test_audit_api.py           [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       └── fixtures/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│           ├── sample_policy.txt       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│           ├── sample_dates.txt        [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│           └── sample_mixed_answer.json [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── frontend/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── index.html                      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── package.json                   [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── vite.config.ts                 [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── tsconfig.json                  [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── tsconfig.app.json              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── tsconfig.node.json             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── components.json                [PROPOSED — conditional] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   └── src/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── main.tsx                   [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── App.tsx                    [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── index.css                  [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── api/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── client.ts              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   └── schema.d.ts            [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── pages/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── NewAuditPage.tsx       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   └── AuditResultsPage.tsx   [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── components/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── ui/                    [PROPOSED — directory] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── AppHeader.tsx          [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── AuditForm.tsx           [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── FileDropzone.tsx       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── AuditProgress.tsx      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── AuditSummary.tsx       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── ClaimList.tsx            [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── OriginalAnswerViewer.tsx [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── EvidencePanel.tsx      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── VerdictBadge.tsx       [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── WarningBanner.tsx      [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   └── EmptyState.tsx          [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── hooks/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   └── useAudit.ts             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       ├── lib/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── offsets.ts              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   ├── utils.ts                [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       │   └── labels.ts               [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│       └── tests/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│           ├── offsets.test.ts        [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│           └── verdict-labels.test.ts [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
├── scripts/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── export_openapi.py              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── generate_frontend_types.sh     [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   ├── check_model.py                 [PROPOSED — optional] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
│   └── run_smoke_test.py              [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
└── examples/ [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
    ├── example_source.txt             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
    ├── example_answer.txt             [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
    └── expected_findings.json         [PROPOSED] # [Evidence: exact path appears in the proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]
```

**Tree evidence:** All names in the tree above appeared in the proposed `second-opinion/` repository tree in the architecture blueprint; individual responsibilities and statuses are listed below. [Evidence: full proposed repository tree | where in chat: middle, architecture blueprint, Deliverable 5]

### 8.2 Root-level files

| Path | Purpose | Status | Evidence |
|---|---|---|---|
| `.gitignore` | Ignore caches, generated files, secrets, and local data. | PROPOSED | [Evidence: `.gitignore` in proposed repository tree | architecture blueprint, Deliverable 5] |
| `.env.example` | List environment-variable names without real secrets. | PROPOSED | [Evidence: `.env.example` in proposed repository tree and the secret-handling rule | architecture blueprint; architecture master prompt, §4] |
| `.python-version` | Record the proposed Python runtime baseline. | PROPOSED | [Evidence: `.python-version` in proposed tree | architecture blueprint, Deliverable 5] |
| `pyproject.toml` | Python project/dependency metadata. | PROPOSED | [Evidence: `pyproject.toml` in proposed tree | architecture blueprint, Deliverable 5] |
| `uv.lock` | Lock Python dependencies after an actual successful install. | PROPOSED | [Evidence: “create after a successful Python install” | architecture blueprint, Deliverable 5] |
| `package.json` | Optional workspace scripts. | PROPOSED | [Evidence: “if using npm workspaces” | architecture blueprint, Deliverable 5] |
| `package-lock.json` | Lock npm dependencies after installation. | PROPOSED | [Evidence: “commit after npm install” | architecture blueprint, Deliverable 5] |
| `Dockerfile` | Optional container deployment path. | PROPOSED | [Evidence: “optional public deployment” | architecture blueprint, Deliverable 5] |

### 8.3 Documentation paths

| Path | Purpose | Status | Evidence |
|---|---|---|---|
| `contracts/api-notes.md` | Short human-readable API contract summary. | PROPOSED | [Evidence: “short human contract summary; not README” | architecture blueprint, Deliverable 5] |
| `docs/ARCHITECTURE.md` | Record architecture decisions. | PROPOSED | [Evidence: “architecture decisions” | architecture blueprint, Deliverable 5] |
| `docs/DATA_CONTRACTS.md` | Document request/response fields and offset rules. | PROPOSED | [Evidence: “request/response fields and offset rules” | architecture blueprint, Deliverable 5] |
| `docs/TEST_PLAN.md` | Record labelled tests and evaluation rules. | PROPOSED | [Evidence: “hand-labelled cases and evaluation rules” | architecture blueprint, Deliverable 5] |
| `docs/DEPLOYMENT.md` | Record local and optional deployment instructions. | PROPOSED | [Evidence: “local and optional deployment” | architecture blueprint, Deliverable 5] |

### 8.4 Backend paths

| Path | Purpose | Status | Evidence |
|---|---|---|---|
| `backend/app/__init__.py` | Python package marker. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/app/main.py` | FastAPI application entry and health/static-serving setup. | PROPOSED | [Evidence: “FastAPI app, health route, static frontend mount” | architecture blueprint, Deliverable 5] |
| `backend/app/config.py` | Environment settings, limits, model ID, allowed origins. | PROPOSED | [Evidence: “env values, size limits, model ID, allowed origins” | architecture blueprint, Deliverable 5] |
| `backend/app/errors.py` | Safe error codes and HTTP mappings. | PROPOSED | [Evidence: “safe error codes and HTTP mappings” | architecture blueprint, Deliverable 5] |
| `backend/app/schemas.py` | Canonical Pydantic request/response models. | PROPOSED | [Evidence: “authoritative Pydantic request/response models” | architecture blueprint, Deliverable 5] |
| `backend/app/api/__init__.py` | API package marker. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/app/api/audit_routes.py` | Implement proposed audit and health routes. | PROPOSED | [Evidence: “`POST /api/audits`; `GET /api/health`” | architecture blueprint, Deliverable 5] |
| `backend/app/services/__init__.py` | Services package marker. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/app/services/audit_service.py` | Orchestrate the audit workflow. | PROPOSED | [Evidence: “orchestrates pipeline” | architecture blueprint, Deliverable 5] |
| `backend/app/services/validation.py` | Validate answers, source inputs, files, and size limits. | PROPOSED | [Evidence: “answer/source/file/size validation” | architecture blueprint, Deliverable 5] |
| `backend/app/services/document_parser.py` | Extract canonical text from supported formats. | PROPOSED | [Evidence: “PDF/TXT/DOCX to canonical text” | architecture blueprint, Deliverable 5] |
| `backend/app/services/source_chunks.py` | Chunk source text and preserve provenance ranges. | PROPOSED | [Evidence: “chunking + provenance ranges” | architecture blueprint, Deliverable 5] |
| `backend/app/services/claim_segmenter.py` | Split answer into claim-sized units and offsets. | PROPOSED | [Evidence: “sentences/clauses + original offsets” | architecture blueprint, Deliverable 5] |
| `backend/app/services/retriever.py` | Retrieve source chunks using BM25. | PROPOSED | [Evidence: “BM25 ranking of source chunks” | architecture blueprint, Deliverable 5] |
| `backend/app/services/nli_verifier.py` | Load the proposed NLI model and assess pairs. | PROPOSED | [Evidence: “lazy model loader and pair inference” | architecture blueprint, Deliverable 5] |
| `backend/app/services/rules_verifier.py` | Apply deterministic checks for selected date/number/negation patterns. | PROPOSED | [Evidence: “deterministic match/number/date/negation flags” | architecture blueprint, Deliverable 5] |
| `backend/app/services/verdict_mapper.py` | Map assessment signals into evidence verdicts. | PROPOSED | [Evidence: “combine evidence signals into verdicts” | architecture blueprint, Deliverable 5] |
| `backend/app/services/safety_flags.py` | Optional narrow safety flags kept separate from factuality. | PROPOSED | [Evidence: “optional narrow warning rules” | architecture blueprint, Deliverable 5] |
| `backend/app/services/summary_service.py` | Aggregate finding counts and review status. | PROPOSED | [Evidence: “aggregate counts/review status” | architecture blueprint, Deliverable 5] |
| `backend/app/util/__init__.py` | Utility package marker. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/app/util/hashes.py` | SHA-256 duplicate checks inside one request. | PROPOSED | [Evidence: “SHA-256 duplicate checks per request” | architecture blueprint, Deliverable 5] |
| `backend/app/util/offsets.py` | Validate character ranges and spans. | PROPOSED | [Evidence: “character range and span validation helpers” | architecture blueprint, Deliverable 5] |

### 8.5 Backend tests and fixtures

| Path | Purpose | Status | Evidence |
|---|---|---|---|
| `backend/tests/test_health.py` | Health-endpoint tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/tests/test_parsers.py` | Document-parser tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/tests/test_offsets.py` | Offset and span tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/tests/test_retriever.py` | BM25 retrieval tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/tests/test_verdict_mapper.py` | Verdict mapping tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/tests/test_audit_api.py` | Audit API tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `backend/tests/fixtures/sample_policy.txt` | Synthetic policy-source fixture. | PROPOSED | [Evidence: “synthetic source fixture” | architecture blueprint, Deliverable 5] |
| `backend/tests/fixtures/sample_dates.txt` | Synthetic date-source fixture. | PROPOSED | [Evidence: “synthetic date fixture” | architecture blueprint, Deliverable 5] |
| `backend/tests/fixtures/sample_mixed_answer.json` | Mixed-correctness fixture. | PROPOSED | [Evidence: “mixed-correctness example fixture” | architecture blueprint, Deliverable 5] |

### 8.6 Frontend paths

| Path | Purpose | Status | Evidence |
|---|---|---|---|
| `frontend/index.html` | Frontend HTML entry point. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/package.json` | Frontend dependencies and scripts. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/vite.config.ts` | Vite configuration and proposed API proxy. | PROPOSED | [Evidence: “Vite config and local /api proxy” | architecture blueprint, Deliverable 5] |
| `frontend/tsconfig.json` | TypeScript project configuration. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/tsconfig.app.json` | App-specific TypeScript configuration. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/tsconfig.node.json` | Tooling TypeScript configuration. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/components.json` | Optional shadcn/ui configuration. | PROPOSED | [Evidence: “shadcn/ui config, if used” | architecture blueprint, Deliverable 5] |
| `frontend/src/main.tsx` | React mount. | PROPOSED | [Evidence: “React mount” | architecture blueprint, Deliverable 5] |
| `frontend/src/App.tsx` | Workspace flow and selected-audit state. | PROPOSED | [Evidence: “workspace flow and selected audit state” | architecture blueprint, Deliverable 5] |
| `frontend/src/index.css` | Tailwind import and global design tokens. | PROPOSED | [Evidence: “Tailwind import + global design tokens” | architecture blueprint, Deliverable 5] |
| `frontend/src/api/client.ts` | Fetch wrapper, multipart requests, and error normalisation. | PROPOSED | [Evidence: “fetch wrapper, multipart request, error normalizer” | architecture blueprint, Deliverable 5] |
| `frontend/src/api/schema.d.ts` | Generated TypeScript API types. | PROPOSED | [Evidence: “generated from FastAPI OpenAPI; do not hand-edit” | architecture blueprint, Deliverable 5] |
| `frontend/src/pages/NewAuditPage.tsx` | Answer/source form. | PROPOSED | [Evidence: “answer/source form” | architecture blueprint, Deliverable 5] |
| `frontend/src/pages/AuditResultsPage.tsx` | Audit-results workspace. | PROPOSED | [Evidence: “result workspace” | architecture blueprint, Deliverable 5] |
| `frontend/src/components/ui/` | Directory for UI components actually used. | PROPOSED | [Evidence: “only shadcn components actually used” | architecture blueprint, Deliverable 5] |
| `frontend/src/components/AppHeader.tsx` | Application header. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/AuditForm.tsx` | Answer/source input component. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/FileDropzone.tsx` | File upload/drop component. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/AuditProgress.tsx` | Analysis progress display. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/AuditSummary.tsx` | Aggregate audit summary. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/ClaimList.tsx` | List of claim-level findings. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/OriginalAnswerViewer.tsx` | Original answer and highlights. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/EvidencePanel.tsx` | Evidence passage inspector. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/VerdictBadge.tsx` | User-facing verdict badge. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/WarningBanner.tsx` | Warning/limitations panel. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/components/EmptyState.tsx` | Empty/initial state. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/hooks/useAudit.ts` | Loading, error, and result state. | PROPOSED | [Evidence: “loading/error/result state” | architecture blueprint, Deliverable 5] |
| `frontend/src/lib/offsets.ts` | Convert backend code-point offsets to JavaScript UTF-16 indexes. | PROPOSED | [Evidence: “code-point offsets → JS UTF-16 indexes” | architecture blueprint, Deliverable 5] |
| `frontend/src/lib/utils.ts` | Proposed class-name and formatting helpers. | PROPOSED | [Evidence: “cn helper, formatting” | architecture blueprint, Deliverable 5] |
| `frontend/src/lib/labels.ts` | Map internal verdict values to user-facing labels. | PROPOSED | [Evidence: “user-friendly verdict labels” | architecture blueprint, Deliverable 5] |
| `frontend/src/tests/offsets.test.ts` | Frontend offset tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |
| `frontend/src/tests/verdict-labels.test.ts` | Verdict-label tests. | PROPOSED | [Evidence: exact path in proposed tree | architecture blueprint, Deliverable 5] |

### 8.7 Scripts and example files

| Path | Purpose | Status | Evidence |
|---|---|---|---|
| `scripts/export_openapi.py` | Export the FastAPI OpenAPI schema. | PROPOSED | [Evidence: “export backend OpenAPI schema” | architecture blueprint, Deliverable 5] |
| `scripts/generate_frontend_types.sh` | Generate frontend types from OpenAPI. | PROPOSED | [Evidence: “create frontend API types from OpenAPI” | architecture blueprint, Deliverable 5] |
| `scripts/check_model.py` | Check model loading and inspect the label map. | PROPOSED | [Evidence: “download/load primary model and print label map” | architecture blueprint, Deliverable 5] |
| `scripts/run_smoke_test.py` | Run a sample audit. | PROPOSED | [Evidence: “one sample source-answer audit” | architecture blueprint, Deliverable 5] |
| `examples/example_source.txt` | Synthetic reference source. | PROPOSED | [Evidence: “synthetic example source, no personal data” | architecture blueprint, Deliverable 5] |
| `examples/example_answer.txt` | Example answer with mixed correctness. | PROPOSED | [Evidence: “expected mixed-correctness answer” | architecture blueprint, Deliverable 5] |
| `examples/expected_findings.json` | Hand-labelled expected result. | PROPOSED | [Evidence: “hand-labelled expected result” | architecture blueprint, Deliverable 5] |

### 8.8 Optional future paths, excluded from the MVP tree

| Exact spelling from chat | Purpose | Status | Evidence |
|---|---|---|---|
| `backend/app/db.py` | Possible future database connection/module. | PROPOSED, not for MVP | [Evidence: “If persistent single-user local history becomes mandatory, add `backend/app/db.py`” | architecture blueprint, optional SQLite extension] |
| `backend/app/db_models.py` | Possible future database models. | PROPOSED, not for MVP | [Evidence: “add `backend/app/db.py`, `backend/app/db_models.py`” | architecture blueprint, optional SQLite extension] |
| `a migration script` | A possible migration script; exact filename was not provided. | PROPOSED; filename NOT SPECIFIED IN CHAT | [Evidence: “a migration script” | architecture blueprint, optional SQLite extension] |

The optional database paths appeared without the repository prefix. Their full rooted locations are **INFERRED, needs confirmation** and are not silently normalised here. [Evidence: the optional-extension paragraph spells them as `backend/app/db.py` and `backend/app/db_models.py` while the primary tree uses `second-opinion/` | where in chat: middle, architecture blueprint]

## 9. Detailed Implementation

**Implementation status:** The described modules remain planned. No actual code implementation or successful test was confirmed. **Status: IMPLEMENTED as a project-state fact.** [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

### 9.1 Input collection and validation

The user submits the original AI-generated answer and pasted source text and/or files; the architecture requires non-empty answer text and at least one non-empty readable source. **Status: DECIDED requirement; PROPOSED implementation.** [Evidence: Stage 2 answer 4; architecture blueprint, `POST /api/audits` contract]

The architecture proposed caps of answer ≤ 40,000 characters, up to five files, 10 MiB per file, extracted source ≤ 150,000 characters, and a suggested claim cap such as 50. These values have not been tested or confirmed as final settings. **Status: PROPOSED.** [Evidence: “Caps: suggested defaults” | where in chat: middle, architecture blueprint, API contract]

### 9.2 Document parsing

The selected file types for the starting direction are PDF, DOCX, and TXT. [Evidence: “pypdf + python-docx + TXT support” | where in chat: late, Stage 2 answer 3]

The proposed parser extracts text and records source identity and page information where available. The blueprint says PDF page numbering is 1-based and may be `null` for pasted text/DOCX when reliable page metadata is not available. **Status: PROPOSED.** [Evidence: “PDF page number is 1-based” and “page number is `null` unless reliable page metadata exists” | where in chat: middle, architecture blueprint, data-contract principles]

Scanned-PDF OCR is deferred and must not be represented as available until it is implemented and tested. **Status: DECIDED.** [Evidence: “Do not promise OCR capabilities unless they can be tested” | where in chat: middle, architecture master prompt, §5D]

### 9.3 Source preparation and chunking

The blueprint proposed paragraph-aware chunks of approximately 120–220 words with around 40 words of overlap, preserving source character offsets and page metadata where available. These are proposed starting parameters, not measured optimal values. **Status: PROPOSED.** [Evidence: “approximately 120–220 word chunks with around 40 words overlap” | where in chat: middle, architecture blueprint, request lifecycle]

### 9.4 Claim segmentation

The latest user-confirmed direction is deterministic sentence/paragraph splitting with source offsets. **Status: DECIDED.** [Evidence: “Deterministic sentence/paragraph chunking with source offsets” | where in chat: late, Stage 2 answer 3]

The architecture also proposed splitting only simple, independently predicated coordinated clauses when safe, preserving the parent sentence, and otherwise keeping a whole compound sentence for review. **Status: PROPOSED.** [Evidence: the claim-segmentation rules in architecture blueprint, P0 scope and `Claim` model]

The blueprint initially proposed spaCy `en_core_web_sm`; the later cost audit proposed deterministic sentence splitting as a replacement for the first implementation. The latter is the newer proposal, but the selected user stack specifies deterministic splitting. **Status: PROPOSED for spaCy; DECIDED for deterministic splitting.** [Evidence: “spaCy `en_core_web_sm`” in architecture blueprint; “Deterministic sentence/paragraph splitter preserving offsets” in cost audit; user confirms deterministic splitting in Stage 2 answer 3]

### 9.5 Evidence retrieval

BM25 is the selected initial retrieval approach. **Status: DECIDED.** [Evidence: “Retrieval: BM25” | where in chat: late, Stage 2 answer 3]

The blueprint proposed retrieving the top three candidate passages per claim, using up to five for small sources. These are suggested parameters that require testing. **Status: PROPOSED.** [Evidence: “keep top 3 candidates per claim (up to 5 for small sources)” | where in chat: middle, architecture blueprint]

The system must not treat lexical similarity alone as entailment. **Status: DECIDED.** [Evidence: “Do not treat a passage as supporting evidence merely because it contains similar words” | where in chat: middle, architecture master prompt, §6]

### 9.6 NLI assessment

The proposed exact model is `microsoft/deberta-base-mnli`. **Status: PROPOSED.** [Evidence: “Primary local verifier: `microsoft/deberta-base-mnli`” | where in chat: middle, architecture blueprint]

The model is intended to compare a source passage as the premise and the submitted claim as the hypothesis, returning NLI class scores. **Status: PROPOSED.** [Evidence: “Run evidence as premise and claim as hypothesis” | where in chat: middle, architecture blueprint, local model comparison]

The model must not be regarded as an independent truth authority, and its output must not be described as a calibrated truth probability. **Status: DECIDED.** [Evidence: “not as an independent authority on truth” | where in chat: late, Stage 2 answer 5; “not display softmax as probability true” | architecture blueprint]

The blueprint proposes inspecting the actual model label map at runtime rather than assuming fixed numeric class positions. **Status: PROPOSED.** [Evidence: “inspect the model’s actual `id2label` mapping at runtime” | where in chat: middle, architecture blueprint]

### 9.7 Rules and verdict mapping

Deterministic checks for date, number, negation, and obvious arithmetic discrepancies were suggested as incremental enhancements. **Status: PROPOSED.** [Evidence: “Heuristic date/number/negation discrepancy flags” and “Detect obvious arithmetic inconsistencies” | where in chat: middle, architecture blueprint, P1 scope]

The proposed factual verdict categories are `SUPPORTED_BY_SOURCE`, `CONTRADICTED_BY_SOURCE`, `NOT_ESTABLISHED_BY_SOURCE`, and `AMBIGUOUS_OR_CONFLICTING`. **Status: PROPOSED as exact strings; DECIDED as distinct meanings.** [Evidence: the `ClaimFinding` contract in the architecture blueprint; user's Stage 2 answer 5]

Logic concerns and safety concerns should be separate arrays or fields, not overloaded into the factual verdict. **Status: PROPOSED.** [Evidence: “Separate arrays `logic_concerns` and `safety_concerns`” | where in chat: middle, architecture blueprint, `ClaimFinding`]

### 9.8 Summary and severity

The blueprint proposed counts for total claims, supported claims, contradicted claims, not-established claims, ambiguous claims, logic concerns, and safety concerns. **Status: PROPOSED.** [Evidence: the `AuditSummary` example in architecture blueprint]

The application must not calculate an ungrounded universal accuracy percentage; the summary should display transparent counts and review warnings. **Status: DECIDED.** [Evidence: “Do not invent a universal accuracy percentage” | where in chat: middle, architecture master prompt, §6]

### 9.9 Report export

Exporting/downloading or saving the audit report is required. The precise output format, export filename, and implementation path are not specified. **Status: DECIDED for capability; NOT SPECIFIED IN CHAT for format/path.** [Evidence: “Provide a way to download or save the audit report” | where in chat: late, Stage 2 answer 4]

The architecture blueprint previously proposed JSON export or copying a compact result summary as a P1 item; your Stage 2 answer later confirms export as a required initial capability. The later requirement supersedes the earlier “after P0” prioritisation, but does not settle the format. **Status: DECIDED for export; JSON/copy remain PROPOSED formats.** [Evidence: “Export the audit as JSON or copy a compact result summary” | where in chat: middle, architecture blueprint, P1 scope; “export the audit report” | late, Stage 2 answer 4]

## 10. API, Endpoints, and Data Models

**API implementation status:** No endpoint has been implemented or tested. The paths below are from the proposed architecture contract only. [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

### 10.1 Proposed endpoint list

| Method and path | Purpose | Status | Evidence |
|---|---|---|---|
| `GET /api/health` | Return API readiness, verifier mode, model readiness, and supported file types. | PROPOSED | [Evidence: endpoint contract in architecture blueprint | where in chat: middle, Deliverable 7] |
| `POST /api/audits` | Run a source-grounded audit synchronously and return findings/evidence. | PROPOSED | [Evidence: endpoint contract in architecture blueprint | where in chat: middle, Deliverable 7] |

No separate audit-history lookup endpoint is planned for the MVP because server-side persistence was excluded. **Status: DECIDED constraint; PROPOSED API design.** [Evidence: “There is no `GET /api/audits/{id}` history endpoint because audits are not retained on the server” | where in chat: middle, architecture blueprint; later confirmed by Stage 2 answer 4]

### 10.2 Proposed `POST /api/audits` contract

The blueprint proposed `multipart/form-data` with `answer` (required), `source_text` (optional), and `files` (0–5 optional files). At least one non-empty pasted source or successfully extracted file must result. **Status: PROPOSED.** [Evidence: `POST /api/audits` fields in architecture blueprint]

The blueprint proposed these suggested defaults: answer ≤ 40,000 characters; file count ≤ 5; each file ≤ 10 MiB; extracted source ≤ 150,000 characters; suggested claim cap such as 50; do not silently truncate. **Status: PROPOSED; exact final limits NOT SPECIFIED IN CHAT.** [Evidence: “Caps: suggested defaults” | where in chat: middle, architecture blueprint]

The proposed success response is an `AuditResponse` containing an audit ID, status, `source_mode`, original answer, source metadata, findings, summary, warnings, engine metadata, and creation time. **Status: PROPOSED.** [Evidence: `AuditResponse` JSON example | where in chat: middle, architecture blueprint]

The proposed structured error codes include `ANSWER_EMPTY`, `FILE_TOO_LARGE`, `CONTENT_TOO_LARGE`, `UNSUPPORTED_FILE_TYPE`, `SOURCE_EMPTY_OR_UNREADABLE`, `INVALID_INPUT`, `RATE_LIMITED`, and `AUDIT_FAILED`. **Status: PROPOSED.** [Evidence: validation errors list | where in chat: middle, architecture blueprint]

### 10.3 Proposed data models

The following model names were explicitly present in the blueprint. They are proposed contracts, not implemented schemas. **Status: PROPOSED.** [Evidence: “Core models” in architecture blueprint, Deliverable 6]

- **`SourceDocument`** — proposed fields include `source_id`, `filename`, `media_type`, `sha256`, `character_count`, `page_count`, `extraction_status`, and `warnings`. [Evidence: `SourceDocument` JSON example | where in chat: middle, architecture blueprint]
- **`SourceChunk`** — proposed fields include `chunk_id`, `source_id`, `text`, `start_char`, `end_char`, `page_number`, `section`, and optional `retrieval_score`. [Evidence: `SourceChunk` JSON example | where in chat: middle, architecture blueprint]
- **`Claim`** — proposed fields include `claim_id`, `text`, original-answer offsets, `parent_sentence`, `compound_claim_review`, and `flags`. [Evidence: `Claim` JSON example | where in chat: middle, architecture blueprint]
- **`EvidenceReference`** — proposed fields include `evidence_id`, `source_id`, `source_name`, exact `quote`, page/section, source offsets, relation, and retrieval rank. [Evidence: `EvidenceReference` JSON example | where in chat: middle, architecture blueprint]
- **`ClaimFinding`** — proposed fields include `claim_id`, `verdict`, `explanation`, evidence, `logic_concerns`, `safety_concerns`, `review_priority`, `evidence_strength`, model details, and warnings. [Evidence: `ClaimFinding` JSON example | where in chat: middle, architecture blueprint]
- **`AuditSummary`** — proposed fields include assessment, review recommendation, claim counts, concern counts, and summary text. [Evidence: `AuditSummary` JSON example | where in chat: middle, architecture blueprint]
- **`AuditResponse`** — proposed fields include `audit_id`, `status`, `source_mode`, `original_answer`, sources, findings, summary, warnings, engine metadata, and `created_at`. [Evidence: `AuditResponse` JSON example | where in chat: middle, architecture blueprint]

### 10.4 Offset rules

The blueprint proposes zero-based, end-exclusive Unicode code-point offsets in the original answer, followed by a frontend conversion to JavaScript UTF-16 indexes before slicing. **Status: PROPOSED.** [Evidence: “zero-based, end-exclusive Unicode code-point offsets” and “converts those to UTF-16 offsets” | where in chat: middle, architecture blueprint]

The original answer should not be trimmed, normalised, reflowed, or rewritten after offsets are calculated. **Status: DECIDED product requirement.** [Evidence: “Do not normalize, trim, reflow, or rewrite the original answer after calculating offsets” | where in chat: middle, architecture blueprint]

## 11. Prompts and AI Logic

### 11.1 Product-auditing logic

The proposed NLI pair construction is: source passage as premise, claim as hypothesis. The model produces NLI class scores rather than an independent statement of truth. **Status: PROPOSED.** [Evidence: “evidence as premise and claim as hypothesis” | where in chat: middle, architecture blueprint]

The audit should treat evidence as untrusted data; an uploaded source that contains instructions to ignore the audit task must not override the intended auditing objective. **Status: DECIDED.** [Evidence: “treat such text as evidence to assess, not instructions that override the system” | where in chat: middle, architecture master prompt, §12]

### 11.2 Coding-agent handoff prompt

An earlier assistant response supplied this text as a copy/paste prompt for coding agents; it was not confirmed as a prompt embedded in the application. [Evidence: assistant supplied a copy/paste coding-agent prompt in the initial research-audit response | where in chat: early, research-audit response]

> Build Second Opinion as an evidence-first AI answer auditor. For each claim preserve original context and distinguish SUPPORTED, CONTRADICTED, NOT_ESTABLISHED_BY_PROVIDED_SOURCES, AMBIGUOUS_OR_CONFLICTING. Assess reasoning issues and safety concerns separately from factual support. Link every finding to relevant source passages and explain why evidence does or does not support claim. Never treat missing evidence as proof of falsity, invent citations, or present an uncalibrated model score as probability of truth. Keep core prototype within no-budget constraint, check model licences and API terms, and evaluate on transparent test set with false-positive cases. Do not claim novelty or superiority without comparative evidence.

**Status: IMPLEMENTED as a quoted planning prompt in the chat; PROPOSED as a coding-agent instruction; not an in-app prompt.** [Evidence: assistant supplied this copy/paste prompt in the earlier research-audit response | where in chat: early research-audit response]

### 11.3 Exact in-application system prompt

An exact production prompt embedded in the application is **NOT SPECIFIED IN CHAT**. The proposed blueprint focuses on local NLI plus deterministic rules and does not establish a general-purpose hosted LLM prompt for core auditing. [Evidence: user confirmed external APIs are “Not required for the core source-grounded audit” | where in chat: late, Stage 2 answer 3]

## 12. Setup and Run Instructions

### 12.1 Current setup status

No clean install or project run has been confirmed. **Status: IMPLEMENTED as a project-state fact.** [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

The repository URL, installed package versions, lockfiles, verified environment-variable names, model-cache path, and exact local run commands are **NOT SPECIFIED IN CHAT** as tested project setup details. [Evidence: “no repository yet”; “None available”; architecture states lockfiles should be generated during scaffold | where in chat: late, Stage 2 answers 1 and 8; middle, architecture blueprint]

### 12.2 Commands that actually appeared in the chat

The following command appeared verbatim in the architecture blueprint as a deployment/build step. [Evidence: “Build React assets (`npm run build`).” | where in chat: middle, architecture blueprint, deployment plan]

```text
npm run build
```

**Status: PROPOSED command; not confirmed to have been run.** [Evidence: “Build React assets (`npm run build`).” | where in chat: middle, architecture blueprint, deployment plan]

No other exact install/run command is recorded here because the project-specific successful install procedure was not established in the available chat. The future implementation must not report a command as tested until it has actually been run. [Evidence: “Do not report implementation progress … until they have been demonstrated through actual execution and testing” | where in chat: late, Stage 2 answer 9]

### 12.3 Environment variables

An `.env.example` was proposed, but the exact final environment-variable names are **NOT SPECIFIED IN CHAT** as a verified application configuration. [Evidence: `.env.example` is proposed in the architecture tree; no real environment file or configuration was supplied | where in chat: middle, architecture blueprint; late, Stage 2 answer 8]

Secrets must not be hard-coded into frontend code, public repositories, or committed configuration files. **Status: DECIDED.** [Evidence: “No API keys may be hard-coded into frontend code, public repositories or committed configuration files” | where in chat: middle, architecture master prompt, §4]

## 13. Cost and Free-Tier Constraints

### 13.1 Budget constraint

The MVP must not require paid services. The project budget is ₹0. **Status: DECIDED.** [Evidence: “Budget: ₹0. Do not recommend paid services as dependencies for the minimum viable product” | where in chat: middle, architecture master prompt, §4]

### 13.2 Local-first runtime

The core audit path must work without an API key, a paid API, or an externally hosted LLM. **Status: DECIDED.** [Evidence: “the core source-grounded auditing workflow must work without a paid API or externally hosted LLM” | where in chat: late, Stage 2 answer 5]

Local inference may require downloading model weights and sufficient computer resources; actual performance and reliability have not been measured. **Status: DECIDED constraint; measurement NOT SPECIFIED IN CHAT.** [Evidence: “Document local model download requirements, hardware limitations and first-run behaviour” and “performance and reliability must be tested rather than assumed” | where in chat: late, Stage 2 answer 5]

### 13.3 Provider/host assumptions explicitly corrected

- The architecture blueprint initially stated that Hugging Face Inference Providers offered free users $0.10 in monthly credits; the later cost audit explicitly marked that statement outdated and said to remove it. The latest chat record is the cost audit’s correction, but current limits must still be re-verified before use. **Status: IMPLEMENTED as a recorded correction.** [Evidence: “replace the blueprint's outdated `$0.10/month credits` statement” | where in chat: late, cost audit]
- Gemini was discussed as an optional provider, but it must not be necessary for the core audit. **Status: DECIDED.** [Evidence: “Hosted models may be considered optional enhancements” | where in chat: late, Stage 2 answer 5]
- Render Free and free Hugging Face Docker/standard Gradio deployment were flagged in the cost audit as not dependable assumptions for a full model-backed public application. **Status: IMPLEMENTED as the result of a cost-audit note; current conditions require verification before deployment.** [Evidence: “that advice is outdated/wrong for a no-budget deployment” | where in chat: late, cost audit]
- The public deployment is optional after local end-to-end validation. **Status: DECIDED.** [Evidence: “Attempt a public deployment only if a genuinely free, suitable host can be verified” | where in chat: late, Stage 2 answer 6]

### 13.4 What is not known

Exact free-tier request counts, storage quotas, trial expiry, current provider rate limits, and credit-card requirements are **NOT SPECIFIED IN CHAT** as final verified configuration values. They must be checked on official provider pages before optional services are used. [Evidence: “Do not assume … all free API tiers … offer unlimited access” | where in chat: middle, architecture master prompt, §4]

## 14. Decisions Log

| Decision or change | Current status | Explanation and evidence |
|---|---|---|
| Product is an evidence-grounded AI answer auditor. | active — DECIDED | [Evidence: “Second Opinion — Evidence-Grounded AI Answer Auditor” | where in chat: late, architecture master prompt, §2] |
| Source-provided audit is the core mode. | active — DECIDED | [Evidence: “do not silently mix claims verified against uploaded sources with claims assessed against external web evidence” | where in chat: middle, architecture master prompt, §6] |
| The starting stack is React + TypeScript + Vite, Python + FastAPI, local DeBERTa NLI as optional signal, BM25, deterministic text splitting, pypdf, python-docx, TXT support. | active — DECIDED starting direction | [Evidence: full stack list | where in chat: late, Stage 2 answer 3] |
| DeBERTa is not a truth oracle. | active — DECIDED | [Evidence: “not as an independent authority on truth” | where in chat: late, Stage 2 answer 5] |
| No external API is required for core functionality. | active — DECIDED | [Evidence: “External APIs: Not required for the core source-grounded audit” | where in chat: late, Stage 2 answer 3] |
| No database, authentication, or persistent server-side history in the first implementation. | active — DECIDED | [Evidence: “Do not introduce a database, authentication system or persistent server-side audit history” | where in chat: late, Stage 2 answer 4] |
| Add export/download capability for audit results. | active — DECIDED | [Evidence: “Provide a way to download or save the audit report” | where in chat: late, Stage 2 answer 4] |
| Local-first demo before public hosting. | active — DECIDED | [Evidence: “Develop and validate the complete application locally first” | where in chat: late, Stage 2 answer 6] |
| Original 14-hour window is a planning constraint, but exact remaining time is unconfirmed. | active — DECIDED | [Evidence: “Use the original approximately 14-hour hackathon window … exact remaining time as unconfirmed” | where in chat: late, Stage 2 answer 10] |
| Git pushes approximately every three hours. | active — DECIDED | [Evidence: “push the code every three hours” | where in chat: early, initial project request; reaffirmed Stage 2 answer 10] |
| spaCy `en_core_web_sm` as segmenter. | superseded — PROPOSED | [Evidence: earlier architecture proposed spaCy; later cost audit proposed deterministic splitter and the user confirmed deterministic splitting | where in chat: middle, architecture blueprint; late, cost audit and Stage 2 answer 3] |
| Hugging Face free-user $0.10 credit statement. | superseded — IMPLEMENTED correction | [Evidence: “outdated `$0.10/month credits` statement” | where in chat: late, cost audit] |
| Free Docker Space treated as a reliable public full-stack host. | superseded — PROPOSED, no longer recommended as assumption | [Evidence: “do not treat … as a guaranteed free deployment option” | where in chat: late, cost audit] |
| Database/history in first build. | superseded — DROPPED for initial MVP | [Evidence: “Do not introduce a database” | where in chat: late, Stage 2 answer 4] |
| Hosted LLM as required core service. | superseded — DROPPED | [Evidence: “the core … workflow must work without … externally hosted LLM” | where in chat: late, Stage 2 answer 5] |
| README creation deferred. | superseded — DECIDED to create now through the staged workflow | [Evidence: earlier architecture prompt said “Do not generate `README.md` yet”; later user requested the README workflow | where in chat: middle and late messages] |

## 15. Known Issues, Bugs, and Fixes

### 15.1 Research attribution issue

Report A attributes a cross-entropy/formal-derivability criticism to Report B, but that specific claim was not found in the separately supplied Report B text discussed in the conversation. The attribution cannot be verified against the supplied Report B version and should not be repeated as a confirmed error without identifying another source/version. **Status: IMPLEMENTED as a recorded research finding.** [Evidence: Report A §3.6 and the prior audit conclusion that the specific claim did not appear in Report B | where in chat: early research-audit exchange]

### 15.2 Generalising the EBU/BBC statistic

The research specifically warns not to present the EBU/BBC 45% result as a rate applying to all AI-generated answers. **Status: DECIDED.** [Evidence: “Do not claim the 45% EBU result applies to all AI-generated answers” | where in chat: late, architecture master prompt, §18]

### 15.3 Missing evidence versus contradiction

An empty retrieval result must not automatically cause a “false” verdict. **Status: DECIDED.** [Evidence: “It must not automatically label an unsupported claim as false” | where in chat: late, architecture master prompt, §2]

### 15.4 Lexical similarity versus support

A source passage containing similar terms does not by itself establish a claim. **Status: DECIDED.** [Evidence: “Do not treat a passage as supporting evidence merely because it contains similar words” | where in chat: middle, architecture master prompt, §6]

### 15.5 Unicode highlight offsets

The proposed architecture warns that backend Unicode code-point offsets differ from JavaScript UTF-16 string indexes. An explicit conversion was proposed, but the fix has not been implemented or tested. **Status: PROPOSED.** [Evidence: “code-point offsets → JS UTF-16 indexes” | where in chat: middle, architecture blueprint]

### 15.6 Model fallback

The proposed rules-only fallback must warn the user if the NLI model fails to load. It must not present the reduced mode as model-backed verification. **Status: PROPOSED.** [Evidence: “Rules-only mode adds a visible warning” | where in chat: middle, architecture blueprint]

### 15.7 Hosting cost and persistence

The cost audit flagged the assumption that a free host will persist files or keep a model-backed service always active. The deployment must be validated rather than assumed. **Status: IMPLEMENTED as a recorded cost-audit finding.** [Evidence: “Do not suggest that a database, uploaded file or model will persist on a hosting platform unless the service documentation supports that behaviour” | where in chat: middle, architecture master prompt, §14]

### 15.8 Actual application bugs

No application runtime bug has been confirmed because no implementation code has been supplied or tested. **Status: IMPLEMENTED as a project-state fact.** [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

## 16. Roadmap (Done / In Progress / Planned / Ideas)

The roadmap below describes project status from the available conversation, not an assumed progress report. [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

### Done

- Research reports were supplied and reviewed in the conversation. **Status: IMPLEMENTED.** [Evidence: two attached research reports and the research audit deliverable | where in chat: early research-audit exchange]
- Architecture blueprint was generated as a planning artifact. **Status: IMPLEMENTED.** [Evidence: “Download the complete blueprint” | where in chat: architecture response]
- Cost audit was generated as a planning artifact. **Status: IMPLEMENTED.** [Evidence: “Download the complete cost audit” | where in chat: cost-audit response]
- The project objective, intended audience, initial technology direction, no-database constraint, no-required-external-API constraint, local-first deployment priority, and report export requirement were confirmed in Stage 2. **Status: IMPLEMENTED as documented decisions.** [Evidence: Stage 2 answers 3–8 | where in chat: late, Stage 2]
- This evidence-tagged README has been created as a working document artifact. **Status: IMPLEMENTED as a documentation artifact; it is not evidence of an application repository.** [Evidence: file created for the current README task | where in chat: this README-writing step]

### In progress

No application implementation activity is confirmed as in progress. **Status: IMPLEMENTED as a status finding.** [Evidence: “Not tested yet” | where in chat: late, Stage 2 answer 9]

### Planned

- Create a clean implementation repository. **Status: DECIDED requirement; not yet performed.** [Evidence: “Start with a clean project structure” | where in chat: late, Stage 2 answer 8]
- Build the frontend/backend skeleton and connect the API. **Status: PROPOSED.** [Evidence: architecture blueprint, Hours 0–3 milestone]
- Implement document extraction for PDF, DOCX, and TXT. **Status: DECIDED requirement; PROPOSED implementation.** [Evidence: Stage 2 answer 3]
- Implement deterministic claim splitting and BM25 evidence retrieval. **Status: DECIDED starting stack direction.** [Evidence: Stage 2 answer 3]
- Integrate local DeBERTa NLI as an optional assessment signal and verify model loading/label mapping. **Status: DECIDED starting direction for optional local signal; PROPOSED exact integration.** [Evidence: Stage 2 answers 3 and 5; architecture blueprint]
- Implement distinct verdicts, source evidence, highlighted original text, visible warnings, and audit report export. **Status: DECIDED requirements; not yet implemented.** [Evidence: Stage 2 answers 4–5 and 7]
- Create and run a small labelled evaluation set before reporting any performance. **Status: DECIDED requirement.** [Evidence: architecture master prompt, §10; Stage 2 answer 9]
- Commit/push meaningful changes approximately every three hours during the hackathon. **Status: DECIDED requirement.** [Evidence: initial project request and Stage 2 answer 10]
- Attempt public deployment only if a suitable genuinely free option is verified and the local demo is stable. **Status: DECIDED requirement.** [Evidence: Stage 2 answer 6]

### Ideas / optional enhancements

- LettuceDetect span-level detection. **Status: PROPOSED.** [Evidence: architecture blueprint, P2 scope]
- Embedding-based retrieval if tests show BM25 misses relevant paraphrases. **Status: PROPOSED.** [Evidence: architecture blueprint, P2 scope]
- External-web verification in a separately labelled mode. **Status: PROPOSED.** [Evidence: architecture master prompt, §6]
- Multilingual support, including relevant Indian languages, after evaluation. **Status: PROPOSED.** [Evidence: architecture master prompt, §5A; architecture blueprint, P2 scope]
- OCR for scanned PDFs. **Status: PROPOSED.** [Evidence: architecture blueprint, P2 scope]
- Persistent history, authentication, team workspaces, and background jobs. **Status: DROPPED from the initial MVP; future options only.** [Evidence: architecture blueprint, P2 scope; Stage 2 answer 4 supersedes the initial database option]

## 17. Open Questions

Each entry below remains unresolved in the chat and must be answered before its details can be stated as settled facts. [Evidence: “If something is missing, unclear, or never decided, write ‘NOT SPECIFIED IN CHAT’” | where in chat: late, README master prompt, No-Invention Rule]

1. **Repository URL and name:** NOT SPECIFIED IN CHAT. There is no repository yet. [Evidence: “no repository yet” | where in chat: late, Stage 2 answer 1]
2. **Literal repository root path:** NOT SPECIFIED IN CHAT. The blueprint proposed `second-opinion/`, but that directory has not been created. [Evidence: proposed tree and “Start with a clean project structure” | where in chat: middle, architecture blueprint; late, Stage 2 answer 8]
3. **Final root location of `README.md`:** NOT SPECIFIED IN CHAT as a literal repository path. This README is produced as a separate artifact for placement into the eventual project root. [Evidence: `README.md` was previously excluded from the proposed tree and is now requested; no repository yet | where in chat: middle and late]
4. **Exact dependency versions:** NOT SPECIFIED IN CHAT as installed/verified versions. The architecture proposed Python 3.11.x and Node 22.x LTS but no install test was performed. [Evidence: architecture blueprint runtime/version policy; Stage 2 answer 9]
5. **Final dependency manifests and lockfiles:** NOT SPECIFIED IN CHAT as created files. [Evidence: architecture blueprint says to create actual lockfiles during scaffold/install]
6. **Exact environment-variable names:** NOT SPECIFIED IN CHAT as confirmed application configuration. [Evidence: `.env.example` is proposed but not implemented]
7. **Exact run/install commands:** NOT SPECIFIED IN CHAT as tested commands, apart from the proposed `npm run build`. [Evidence: architecture blueprint deployment plan; Stage 2 answer 9]
8. **Exact output format for report export:** NOT SPECIFIED IN CHAT. JSON and copying a compact summary were proposed, while the user confirmed the export capability without specifying the format. [Evidence: architecture blueprint P1 scope; Stage 2 answer 4]
9. **Model hardware requirements and measured latency:** NOT SPECIFIED IN CHAT. [Evidence: “performance and reliability must be tested rather than assumed” | where in chat: late, Stage 2 answer 5]
10. **Model threshold values:** NOT SPECIFIED IN CHAT as validated thresholds. [Evidence: architecture says thresholds must be tuned against the labelled test set]
11. **Measured accuracy, precision, recall, F1, or span scores for the actual app:** NOT SPECIFIED IN CHAT. [Evidence: “Do not report … performance results until they have been demonstrated” | where in chat: late, Stage 2 answer 9]
12. **Final public host and live URL:** NOT SPECIFIED IN CHAT. [Evidence: “Attempt a public deployment only if … verified” | where in chat: late, Stage 2 answer 6]
13. **Project-code licence:** NOT SPECIFIED IN CHAT. [Evidence: cost audit says choose a project licence after team agreement]
14. **Exact design tokens, fonts, colour values and component installation:** NOT SPECIFIED IN CHAT as an accepted implemented design. The “calm forensic workspace” is a proposal. [Evidence: architecture blueprint UI specification]
15. **Exact user-defined source/document limits:** NOT SPECIFIED IN CHAT as final accepted values. The architecture's limits are labelled suggested defaults. [Evidence: architecture blueprint API contract]
16. **Detailed safety taxonomy and supported high-stakes domains:** NOT SPECIFIED IN CHAT beyond separate potential safety concerns and a warning not to present this as certified professional advice. [Evidence: architecture master prompt, §6; Stage 2 answer 7]
17. **Final competition rubric and exact submission time:** NOT SPECIFIED IN CHAT. The original approximately 14-hour window is only a planning constraint. [Evidence: Stage 2 answer 10]
18. **Which artifact is the canonical architecture blueprint:** NOT SPECIFIED IN CHAT between `Second_Opinion_Architecture_Blueprint.md` and `Second_Opinion_Architecture_Blueprint_2026-10-10.md`. [Evidence: both file names appeared in the inspected environment]
19. **Exact relationship between similarly named pasted research files:** NOT SPECIFIED IN CHAT. [Evidence: `Pasted text(6).txt`, `Pasted text(5).txt`, `Pasted text(4).txt`, and `Pasted text (2)(1).txt` are present but revision relationships were not confirmed]
20. **Full rooted locations for `backend/app/db.py` and `backend/app/db_models.py`:** NOT SPECIFIED IN CHAT; those are optional, excluded database paths. [Evidence: architecture blueprint optional SQLite extension]
21. **Migration script name/path:** NOT SPECIFIED IN CHAT. [Evidence: architecture says only “a migration script”]
22. **Export implementation path/name:** NOT SPECIFIED IN CHAT. [Evidence: the export capability is confirmed, but no file path is specified | Stage 2 answer 4]
23. **Whether external-provider experimentation will be added at all:** NOT SPECIFIED IN CHAT. Hosted models remain optional, not required. [Evidence: Stage 2 answer 5]
24. **Whether the team eventually chooses a different stack:** NOT SPECIFIED IN CHAT. The confirmed stack may be improved if needed. [Evidence: “yes we will improve if needed” | where in chat: late, Stage 2 answer 3]

## 18. Rules for Future AI Sessions

The following rules are confirmed project instructions for future sessions. [Evidence: “Rules for Future AI Sessions” | where in chat: late, README master prompt, §18]

1. Read this README fully before doing anything. **Status: DECIDED.** [Evidence: “Read this README fully before doing anything” | where in chat: late, README master prompt, §18]
2. Never contradict this README without telling the user. **Status: DECIDED.** [Evidence: “Never contradict it without telling me” | where in chat: late, README master prompt, §18]
3. Never change the stack, structure, or decisions without user approval. **Status: DECIDED.** [Evidence: “Never change the stack, structure, or decisions unless I approve” | where in chat: late, README master prompt, §18]
4. After a project change, tell the user exactly which README lines or sections need updating. **Status: DECIDED.** [Evidence: “After any change, tell me exactly which README lines to update” | where in chat: late, README master prompt, §18]
5. If a new instruction conflicts with this README, ask which one takes precedence. **Status: DECIDED.** [Evidence: “If anything here conflicts with my new instructions, ask me which wins” | where in chat: late, README master prompt, §18]
6. Do not claim implementation, testing, deployment, or measured performance until the relevant activity has actually occurred. **Status: DECIDED.** [Evidence: “Do not report implementation progress, working features or performance results until they have been demonstrated through actual execution and testing” | where in chat: late, Stage 2 answer 9]
7. Keep all mandatory audit functionality independent of external API keys. **Status: DECIDED.** [Evidence: “the application must not become unusable when an API key is absent” | where in chat: late, Stage 2 answer 5]
8. Keep the first implementation transient and free of database/authentication/persistent server-side history. **Status: DECIDED.** [Evidence: “Do not introduce a database, authentication system or persistent server-side audit history” | where in chat: late, Stage 2 answer 4]
9. Preserve distinct supported, contradicted, insufficient-evidence, and ambiguous outcomes. **Status: DECIDED.** [Evidence: “Preserve distinct outcomes…” | where in chat: late, Stage 2 answer 5]
10. Never label a claim false solely because the supplied source did not establish it. **Status: DECIDED.** [Evidence: “It must not automatically label an unsupported claim as false” | where in chat: middle, architecture master prompt, §2]
11. Never claim a model score is a truth probability unless calibration has been established. **Status: DECIDED.** [Evidence: “do not communicate uncalibrated model scores as guaranteed probabilities of truth” | where in chat: middle, architecture master prompt, §2]
12. Treat hosted providers and public deployment as optional after the local demo works. **Status: DECIDED.** [Evidence: Stage 2 answers 5 and 6]
13. Maintain Git commits/pushes at approximately three-hour intervals during the hackathon. **Status: DECIDED.** [Evidence: “push the code every three hours” | where in chat: early initial request; reaffirmed Stage 2 answer 10]
14. Check the official provider page before recording current quotas or free-tier limits. **Status: DECIDED.** [Evidence: “Do not assume” current limits and “verify on official site” | where in chat: late, cost-audit request and architecture master prompt, §18]

## 19. Evidence Appendix

### 19.1 Evidence tag convention

Evidence tags use concise quotations or close paraphrases followed by the location in the chat, as required by the README instruction. **Status: DECIDED documentation rule.** [Evidence: “After each fact, add an evidence tag” | where in chat: late, README master prompt, Evidence Rule]

### 19.2 Stage 1 ledger references

The Stage 1 response used section-local ledger identifiers rather than one continuous numeric sequence. This appendix references those identifiers as they appeared in that response. **Status: IMPLEMENTED as a documentation note.** [Evidence: Stage 1 ledger headings A through I and entries A1–I15 | where in chat: Stage 1 fact-ledger response]

| README section | Stage 1 ledger entries supporting it | Evidence |
|---|---|---|
| 1. Project Name and One-Line Pitch | A1, A2, A3, A6, A12, A13 | [Evidence: Stage 1 ledger section A | where in chat: Stage 1 fact-ledger response] |
| 2. Problem Statement | A3–A12 | [Evidence: Stage 1 ledger section A | where in chat: Stage 1 fact-ledger response] |
| 3. Objective and Success Criteria | A3–A12; E1–E13; G11 | [Evidence: Stage 1 ledger sections A, E, G | where in chat: Stage 1 fact-ledger response] |
| 4. Target Users | A13; Stage 2 answer 7 as recorded in the ledger | [Evidence: Stage 2 answer 7 names students/researchers and developers | where in chat: late, Stage 2] |
| 5. Scope (In / Out / Deferred) | E1–E27; H1–H10; Stage 2 answers 4–7 | [Evidence: Stage 1 ledger sections E and H; Stage 2 answers 4–7 | where in chat: Stage 1 and Stage 2] |
| 6. Complete Tech Stack | B1–B33; F14–F18; Stage 2 answers 3 and 5 | [Evidence: Stage 1 ledger sections B/F; Stage 2 answers 3 and 5 | where in chat: Stage 1 and Stage 2] |
| 7. System Architecture | D1–D24; B15–B24; Stage 2 answers 4–6 | [Evidence: Stage 1 ledger sections B and D; Stage 2 answers 4–6 | where in chat: Stage 1 and Stage 2] |
| 8. Full File and Folder Structure | C1–C7; Stage 3 reconstruction | [Evidence: Stage 1 section C and Stage 3 reconstruction | where in chat: Stage 1 and Stage 3] |
| 9. Detailed Implementation | D1–D24; E1–E23; H1–H10 | [Evidence: Stage 1 sections D, E, H | where in chat: Stage 1 fact-ledger response] |
| 10. API, Endpoints, and Data Models | D15–D22; architecture blueprint Deliverables 6–7 | [Evidence: Stage 1 section D and architecture blueprint | where in chat: Stage 1 and architecture response] |
| 11. Prompts and AI Logic | D7–D13; D23; coding-agent prompt in earlier research response | [Evidence: Stage 1 section D and the earlier coding-agent prompt | where in chat: Stage 1 and initial research response] |
| 12. Setup and Run Instructions | B5–B6; C2; Stage 2 answers 1, 8, 9 | [Evidence: Stage 1 sections B/C; Stage 2 answers 1, 8, 9 | where in chat: Stage 1 and Stage 2] |
| 13. Cost and Free-Tier Constraints | B25–B33; F15–F17; G1–G12; I9–I10 | [Evidence: Stage 1 sections B, F, G, I | where in chat: Stage 1 fact-ledger response] |
| 14. Decisions Log | F1–F18; Stage 2 answers 3–10 | [Evidence: Stage 1 section F and Stage 2 answers 3–10 | where in chat: Stage 1 and Stage 2] |
| 15. Known Issues, Bugs, and Fixes | I1–I15 | [Evidence: Stage 1 section I | where in chat: Stage 1 fact-ledger response] |
| 16. Roadmap | H1–H14; Stage 2 answers 4–10 | [Evidence: Stage 1 section H and Stage 2 answers 4–10 | where in chat: Stage 1 and Stage 2] |
| 17. Open Questions | Stage 1 “Things I looked for but did NOT find in the chat”; Stage 2 answers 1–10 | [Evidence: Stage 1 gaps list reconciled by Stage 2 answers | where in chat: Stage 1 and Stage 2] |
| 18. Rules for Future AI Sessions | latest README master prompt, Golden Rules and §18; Stage 2 answers 4–10 | [Evidence: README master prompt §18 and Stage 2 constraints | where in chat: late, README request and Stage 2] |
| 19. Evidence Appendix | latest README master prompt, Stage 4 §19; Stage 1 ledger structure | [Evidence: “Evidence Appendix” requirement and Stage 1 ledger IDs | where in chat: late, README master prompt and Stage 1 response] |

### 19.3 Planning-artifact source register

These paths were present as artifacts in the conversation's working environment; they are research/planning documents rather than application code. [Evidence: the named files were listed in the working environment and linked in prior assistant messages | where in chat: early and middle, research and architecture responses]

| Artifact | Role recorded in chat | Status | Evidence |
|---|---|---|---|
| `/mnt/data/Pasted text(6).txt` | Uploaded research Report A. | IMPLEMENTED | [Evidence: “SECOND OPINION — UNIFIED RESEARCH AUDIT, EXISTING-SOLUTION LANDSCAPE, TECHNICAL GAPS AND INNOVATION BRIEF” | where in chat: early research-audit exchange] |
| `/mnt/data/Pasted text (2)(1).txt` | Uploaded research Report B. | IMPLEMENTED | [Evidence: “Second Opinion — Comprehensive research and problem-discovery report” | where in chat: early research-audit exchange] |
| `/mnt/data/Pasted text(7).txt` | Uploaded architecture master prompt. | IMPLEMENTED | [Evidence: attachment path surfaced with architecture prompt | where in chat: middle] |
| `/mnt/data/Pasted text(8).txt` | Another uploaded copy of the architecture master prompt. | IMPLEMENTED | [Evidence: attachment path surfaced with architecture prompt | where in chat: middle] |
| `/mnt/data/Second_Opinion_Research_Audit_and_AI_Handoff.md` | Earlier research audit and AI handoff. | IMPLEMENTED | [Evidence: assistant linked “Second Opinion Research Audit & AI Handoff” | where in chat: early research-audit response] |
| `/mnt/data/Second_Opinion_Research_Audit_2026-10-10.md` | Dated research-audit artifact. | IMPLEMENTED | [Evidence: artifact was present in the working environment | where in chat: late, Stage 3] |
| `/mnt/data/Second_Opinion_Architecture_Blueprint.md` | Detailed proposed architecture and implementation blueprint. | IMPLEMENTED | [Evidence: assistant linked “Second Opinion Architecture Blueprint” | where in chat: architecture response] |
| `/mnt/data/Second_Opinion_Architecture_Blueprint_2026-10-10.md` | Dated architecture blueprint artifact or variant. Exact revision relationship is NOT SPECIFIED IN CHAT. | IMPLEMENTED as artifact; relationship unclear | [Evidence: both names appeared in the inspected environment | where in chat: late, Stage 3] |
| `/mnt/data/Second_Opinion_Cost_Audit_2026-10-10.md` | Cost, free-tier, licensing, and hosting audit. | IMPLEMENTED | [Evidence: assistant linked “Second Opinion Cost Audit” | where in chat: cost-audit response] |
| `/mnt/data/README.md` | This evidence-tagged project README artifact. | IMPLEMENTED as an artifact; placement in future repository not confirmed | [Evidence: this file was created in response to “Produce one very large, detailed README.md” | where in chat: latest README workflow] |

---

**End of README content.** Project application implementation, tests, public deployment, exact environment configuration, and measured performance remain NOT SPECIFIED IN CHAT or uncompleted according to the latest confirmation. [Evidence: “Not tested yet” and “no repository yet” | where in chat: late, Stage 2 answers 1 and 9]


---

## 20. Implementation and Verification Addendum (2026-10-10)

This section records the verified implementation artifacts, technical decisions, test suites, and repository state established during the hackathon development phases. Existing historical sections (1–19) are preserved unmodified as the baseline specification.

### 20.1 Repository State & Workspace Placement
- **Repository Remote:** `https://github.com/sheldonvibinonmusic/ViSiON-QUEST_college_round.git`, branch `main`. **Status: IMPLEMENTED.** [Evidence: Git push of commit `d5ef064` verified on local machine]
- **Root Placement:** The project implementation resides directly in the root workspace (`c:\Users\Sheldon Pais\OneDrive\Desktop\BNB'26 Second Option`), with top-level directories `backend/`, `frontend/`, `scripts/`, `examples/`, and `contracts/`. **Status: IMPLEMENTED.** [Evidence: User decision B1 confirmed root placement directly]

### 20.2 Verified Tech Stack & Versions
- **Backend:** Python 3.14.2 host virtual environment (`.venv`), FastAPI, Uvicorn, Pydantic v2. **Status: IMPLEMENTED.** [Evidence: verified in `pyproject.toml` and pytest suite]
- **Retrieval Engine:** `rank-bm25` (`BM25Plus` variant to prevent negative IDF scores on small corpora) with tokenization preserving numbers, currency, and dates. **Status: IMPLEMENTED.** [Evidence: `backend/app/services/retriever.py` and `test_retriever.py`]
- **Document Parsers:** `pypdf` for PDF (page provenance tracking), `python-docx` for DOCX (paragraphs and tables), and plain text. **Status: IMPLEMENTED.** [Evidence: `backend/app/services/document_parser.py` and `test_parsers.py`]
- **Segmentation:** Deterministic claim segmentation with abbreviation and decimal guards, quotation boundary preservation, and strict Unicode code-point offset invariant (`answer[start:end] == claim.text`). **Status: IMPLEMENTED.** [Evidence: `backend/app/services/claim_segmenter.py` and `test_offsets.py`]
- **Verification Logic:** Deterministic rules verifier (`rules_verifier.py`) evaluating numerical/currency discrepancies, date conflicts, and polarity/negation clashes, alongside isolated domain safety flags (`safety_flags.py`) for medical, legal, and financial advisories. **Status: IMPLEMENTED.** [Evidence: `backend/app/services/rules_verifier.py` and `test_verdict_mapper.py`]
- **NLI Verifier:** Local DeBERTa NLI adapter (`nli_verifier.py`) with lazy loading for `microsoft/deberta-base-mnli` and graceful fallback to `rules_only` mode (`MODEL_FALLBACK_RULES_ONLY`) when torch/transformers are absent or resources constrained. **Status: IMPLEMENTED.** [Evidence: `backend/app/services/nli_verifier.py` and `scripts/check_model.py`]
- **Frontend:** Node.js LTS v24.20.0, npm 11.19.0, React 19, TypeScript 5.8, Vite 6, Tailwind CSS 4, Lucide React. **Status: IMPLEMENTED.** [Evidence: `frontend/package.json`, Vitest suite, and clean production build]

### 20.3 Verdict Mapping & Summary Contracts
- **Canonical Verdicts:** All claim findings are strictly mapped to one of four canonical verdicts: `SUPPORTED_BY_SOURCE`, `CONTRADICTED_BY_SOURCE`, `NOT_ESTABLISHED_BY_SOURCE`, and `AMBIGUOUS_OR_CONFLICTING`. **Status: IMPLEMENTED.** [Evidence: User approval B4 and `backend/app/services/verdict_mapper.py`]
- **Absence of Evidence:** Confirmed invariant that unestablished claims are assigned `NOT_ESTABLISHED_BY_SOURCE` and never automatically labeled false or contradicted. **Status: IMPLEMENTED.** [Evidence: verified in `test_verdict_mapper.py::test_missing_evidence_is_not_contradicted`]
- **Summary Aggregation:** Findings are aggregated into transparent integer counts without single-percentage score masking. **Status: IMPLEMENTED.** [Evidence: `backend/app/services/summary_service.py`]

### 20.4 Export and Contract Artifacts
- **OpenAPI Contract:** Machine-readable OpenAPI 3.1.0 specification generated and stored at `contracts/openapi.json`. **Status: IMPLEMENTED.** [Evidence: generated via `scripts/export_openapi.py`]
- **Report Export:** Markdown report generation via `POST /api/audits/export/markdown` and JSON download helpers in frontend client. **Status: IMPLEMENTED.** [Evidence: `test_audit_api.py::test_markdown_export`]

### 20.5 Verification & Test Evidence
- **Backend Test Suite:** 23/23 tests passing in `backend/tests/` via pytest (`.\.venv\Scripts\pytest.exe backend/tests -v`). **Status: IMPLEMENTED.**
- **Frontend Test Suite:** 3/3 tests passing in `frontend/src/tests/` via Vitest (`npm --prefix frontend test`). **Status: IMPLEMENTED.**
- **Frontend Production Build:** TypeScript compilation (`tsc -b`) and Vite production bundling succeeded in ~550ms with zero errors. **Status: IMPLEMENTED.**
- **End-to-End Smoke Test:** Full pipeline verified via `scripts/run_smoke_test.py` exercising supported, contradicted, and unestablished claims. **Status: IMPLEMENTED.**
