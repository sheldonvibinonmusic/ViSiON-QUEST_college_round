# Ideas for Approval

This document records architectural, algorithmic, and feature proposals for Second Opinion. In accordance with Rule 6, no idea in this ledger may be implemented without explicit user approval.

| ID | Idea | Problem Solved | Estimated Effort | Cost | Risk | Affected Section | Recommendation | Status |
|---|---|---|---|---|---|---|---|---|
| **IDEA-01** | Regex-based deterministic sentence splitter with abbreviation protection | Prevents splitting sentences on common abbreviations (e.g., "Dr.", "e.g.", "vs.", "Fig.") to keep original character offsets strictly intact without heavy NLP dependencies | Small (1 hr) | ₹0 | Low | §9.4 | adopt | Approved (part of deterministic splitting) |
| **IDEA-02** | Lazy model loading with singleton pattern for DeBERTa | Prevents cold-start delays on startup and allows the entire API/UI to function in rules-only mode if weights are absent or loading fails | Medium (2 hrs) | ₹0 | Low | §9.6, §7.3 | adopt | Approved (fallback design in §7.3) |
| **IDEA-03** | Structured JSON download + copy formatted summary | Satisfies DECIDED report export requirement by giving users both programmatic JSON and human-readable Markdown/clipboard options | Small (1 hr) | ₹0 | Low | §9.9 | adopt | Approved (by user in B4) |
| **IDEA-04** | LettuceDetect fine-grained token-level hallucination detection | Provides sub-sentence span highlighting if NLI sentence-level is too coarse | Large (4+ hrs) | ₹0 (local compute) | Medium (memory/latency) | §5.2, §16 | defer | Defer to post-MVP P2 |
| **IDEA-05** | Dense vector embeddings (e.g. `sentence-transformers`) | Captures semantic paraphrases missed by BM25 lexical keyword matching | Medium (3 hrs) | ₹0 (local compute) | Medium (extra memory & dependencies) | §5.2, §16 | defer | Defer until BM25 evaluation demonstrates misses |
| **IDEA-06** | OCR text extraction for scanned PDF images | Extracts text from non-digital scanned PDFs | Large (4 hrs) | ₹0 (Tesseract) | High (system binary dependency on Windows) | §5.2, §9.2 | reject for MVP | Dropped from MVP |
