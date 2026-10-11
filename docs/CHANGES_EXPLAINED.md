# Second Opinion — Engine Overhaul & Failure Map Fixes (Explained Simply)

This document explains all the improvements made to Second Opinion in plain, simple English that anyone can understand. For each change, we describe what was broken, why it happened, what we changed, which file and function holds the code, and how we proved that it works.

---

### Change 1: Number Swap and Number Format Matcher (F1)
- **What was broken:** Sometimes people swap two numbers, like saying "revenue was \$45M and expenses were \$12M" when the real report said "revenue was \$12M and expenses were \$45M". The old system only checked if the numbers \$45M and \$12M appeared in the text, so it thought everything was fine and gave a passing grade!
- **Why it happened:** The computer was looking at numbers like loose puzzle pieces without noticing which label belonged to which number. Also, it did not know that "\$45M", "45 million", and "45,000,000" are just different ways to write the exact same amount of money.
- **What we changed:** We built a fact-slot binder that attaches each number to its closest word (like "revenue" or "expenses") and converts different number formats into one standard mathematical number. If two numbers match the same label but have different values, it catches the contradiction immediately.
- **Files and functions:** `backend/app/services/fact_slots.py` (`extract_fact_slots`, `compare_fact_slots`) and `backend/app/services/normalizer.py` (`parse_normalized_numbers`).
- **How we proved it:** We wrote tests in `backend/tests/test_accuracy_engine.py` (`test_f1_swapped_numbers_detected`, `test_f1_number_format_equivalences`) that pass completely and verify that swapped revenue numbers trigger a contradiction.

---

### Change 2: Modal Inversion and Recommendation vs Requirement (F2)
- **What was broken:** When a company policy said "employees should register their equipment", an AI answer might assert "employees must register their equipment". The old system called this supported, even though a recommendation is not a strict rule.
- **Why it happened:** The old verifier did not differentiate between strong rule words like "must" or "shall" and gentle suggestion words like "should" or "may".
- **What we changed:** We created a modal strength classifier that grades words into obligations, permissions, recommendations, or prohibitions. When a source recommends an action but an AI claims it is compulsory, the engine downgrades the verdict to ambiguous rather than giving it an unearned green checkmark.
- **Files and functions:** `backend/app/services/modal_negation.py` (`extract_modal_strength`, `check_modal_and_negation`) and `backend/app/services/rules_verifier.py` (`evaluate_rules`).
- **How we proved it:** We verified this in `backend/tests/test_accuracy_engine.py` (`test_f2_modal_should_to_must_downgrade`, `test_f2_modal_prohibition_clash`), showing that "should vs must" correctly avoids a false supported verdict.

---

### Change 3: Fake Entity and Hallucinated Citation Guard (F3)
- **What was broken:** An AI answer could invent a fake law or standard, like "According to RFC 9999, packets are dropped", inside a sentence of real words. Because most of the words matched the source, the old system mistakenly labeled the claim as supported!
- **Why it happened:** The old overlap score averaged all words together, allowing three real words to hide one completely fabricated citation.
- **What we changed:** We added an exact entity checker that extracts legal citations, RFC standards, quoted phrases, and capitalized proper nouns. If an asserted citation or specific named entity does not appear in the evidence, the engine blocks it from ever being marked as supported.
- **Files and functions:** `backend/app/services/entity_checker.py` (`extract_claim_entities`, `check_exact_entities`) and `backend/app/services/verdict_mapper.py` (`map_verdict_for_claim`).
- **How we proved it:** We ran `backend/tests/test_accuracy_engine.py` (`test_f3_hallucinated_citation_rejected`), confirming that fake RFC 9999 drops straight to NOT_ESTABLISHED_BY_SOURCE.

---

### Change 4: Audience and Domain Scope Guardian (F4)
- **What was broken:** An AI could claim a drone permit applies to "commercial operations", when the source document or heading explicitly stated it was only for "recreational hobby" use.
- **Why it happened:** Words like "commercial" and "recreational" describe different categories of people, but the old algorithm did not know they belong to conflicting legal categories.
- **What we changed:** We added a scope alignment checker that inspects claim sentences, evidence quotes, and document section headings for opposing domain pairs like commercial versus recreational, adult versus minor, or public versus private. When a scope mismatch is detected, the engine marks the evidence as conflicting or ambiguous instead of supported.
- **Files and functions:** `backend/app/services/scope_checker.py` (`check_scope_alignment`) and `backend/app/services/source_chunks.py` (`find_active_heading_for_offset`).
- **How we proved it:** We proved this with `backend/tests/test_accuracy_engine.py` (`test_f4_scope_mismatch_commercial_vs_recreational`), which ensures scope swaps do not pass as supported.

---

### Change 5: Directional Opposites and Polarity Clashes (F5)
- **What was broken:** When an AI claimed profits "increased by 15%" while the financial source reported profits "decreased by 15%", or when a claim said "at least 10" while the source said "at most 10", simple keyword matchers could fail to spot the opposition.
- **Why it happened:** Directional words like "increase" and "decrease" share identical financial contexts, so standard search engines score them as very similar instead of opposite.
- **What we changed:** We built an opposite pair dictionary that explicitly links antonym pairs (such as increase/decrease, more/less, before/after, and at least/at most). If the claim uses one direction and the source uses the other, the engine marks it as a direct factual contradiction.
- **Files and functions:** `backend/app/services/modal_negation.py` (`OPPOSITE_PAIRS`, `check_modal_and_negation`).
- **How we proved it:** We proved this in `backend/tests/test_accuracy_engine.py` (`test_f5_directional_opposites_increase_vs_decrease`, `test_f5_directional_opposites_at_least_vs_at_most`).

---

### Change 6: Deterministic Stemming and Synonym Normalizer (F6)
- **What was broken:** If the source said "the company bought servers as demand rose", but the claim said "the company purchased servers as demand increased", the system sometimes failed to connect them because the exact letters were different.
- **Why it happened:** Without a dictionary of common words and word endings (like -ed, -ing, -s), two sentences that say the exact same thing looked like strangers to the computer.
- **What we changed:** We wrote a lightweight, pure-Python stemmer and synonym dictionary that translates words like "bought" to "buy", "purchased" to "buy", and "rose" to "increase", all without needing expensive external APIs or slow downloads.
- **Files and functions:** `backend/app/services/normalizer.py` (`stem_word`, `normalize_token`, `SYNONYM_MAP`, `ABBREVIATIONS_MAP`).
- **How we proved it:** We verified this in `backend/tests/test_accuracy_engine.py` (`test_f6_stemming_and_synonym_normalization`), proving that paraphrased sentences are correctly recognized as supported.

---

### Change 7: Big Document Handling and Scanned PDF Detection (F7)
- **What was broken:** When users uploaded big documents or text larger than 150,000 characters, the server would throw an error and crash the whole audit. Also, if someone uploaded a scanned PDF with pictures instead of selectable text, the auditor gave confusing results.
- **Why it happened:** The server had a strict character wall that rejected anything over 150k characters, and the PDF reader did not warn users that images have no digital text layer.
- **What we changed:** We raised the processing limits to support documents up to 50 megabytes, added safe chunked indexing that keeps the first 150,000 characters with a calm explanation notice, and added automatic detection for image-only scanned PDFs.
- **Files and functions:** `backend/app/services/validation.py` (`validate_extracted_source_length`), `backend/app/services/document_parser.py` (`parse_pdf_bytes`), and `backend/app/services/audit_service.py` (`process_audit`).
- **How we proved it:** We tested a 200,000-character input in `backend/tests/test_accuracy_engine.py` (`test_f7_large_document_processed_without_crash`), proving that it finishes successfully with `truncated=True` and zero crashes.

---

### Change 8: Safe Same-Domain Subpage Web Crawling (F8)
- **What was broken:** When a user submitted a URL, the auditor only looked at the front door page. If the evidence was located on a linked subpage on the exact same website, the auditor missed it completely.
- **Why it happened:** The original URL fetcher only downloaded a single HTML file and ignored internal navigation links.
- **What we changed:** We added a bounded crawler that discovers internal subpages on the same registered domain, follows up to 3 relevant subpages within a tight time budget, strictly checks `robots.txt`, and blocks any private network SSRF attacks on every single link.
- **Files and functions:** `backend/app/services/url_fetcher.py` (`HTMLContentExtractor`, `crawl_and_parse_url`) and `backend/app/services/audit_service.py` (`process_audit`).
- **How we proved it:** We proved this through unit tests in `backend/tests/test_url_fetcher.py` and `test_hostile_server.py`, ensuring robots.txt and SSRF defenses remain completely impenetrable while subpages are safely gathered.

---

### Change 9: Error Isolation and Audit Deadlines (F9)
- **What was broken:** If one strange claim caused an unexpected error or took too long, the entire audit would fail, losing all the work done on the other claims.
- **Why it happened:** The claims loop ran without individual safety shields, so a single problem broke the whole chain.
- **What we changed:** We wrapped each claim evaluation in an isolated safety shield so that an error on one claim is safely caught and noted as an isolated finding while the rest of the audit continues smoothly. We also added an execution deadline that returns partial well-formed findings if the clock runs out.
- **Files and functions:** `backend/app/services/audit_service.py` (`process_audit`) and `backend/app/main.py` (`global_exception_handler`).
- **How we proved it:** We tested timeout limits and exception handling in `backend/tests/test_benchmark_suite.py` and `test_accuracy_engine.py`.

---

### Change 10: Clear "Why This Verdict" Explanations (F10)
- **What was broken:** Users would see a verdict like "Contradicted" or "Ambiguous" but had to guess why the computer came to that conclusion.
- **Why it happened:** The backend created complex internal decisions but only sent back a generic text paragraph without a concise reason or check breakdown.
- **What we changed:** We added clear `verdict_reason` and `checks` fields to every claim finding. The frontend now displays a clean "Why this verdict" summary, section numbers, exact origin badges, and calm notices if documents were truncated or subpages were explored.
- **Files and functions:** `backend/app/schemas.py` (`ClaimFinding`, `AuditResponse`), `frontend/src/components/ClaimList.tsx`, `frontend/src/components/EvidencePanel.tsx`, and `frontend/src/components/AuditSummary.tsx`.
- **How we proved it:** We verified this in `backend/tests/test_accuracy_engine.py` (`test_f10_audit_response_contains_checks_and_reasons`) and confirmed all frontend components build cleanly with 0 TypeScript and linter errors.
