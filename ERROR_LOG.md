# Error Log — Second Opinion Phase 2 Tough Testing

This ledger tracks all vulnerabilities, edge-case failures, and anomalies identified during Phase 2 hostile testing, real public URL audits, and pipeline stress tests.
Schema: `ID | How Found | Severity | Root Cause | Fix | Regression Test | Status`

---

| ID | How Found | Severity | Root Cause | Fix | Regression Test | Status |
|---|---|---|---|---|---|---|
| ERR-001 | Hostile Server Test | High | Missing rejection of embedded credentials in URLs (`user:password@`) allows potential credential leaks and parser confusion | Added username/password validation in `validate_url_and_check_ssrf` | `test_ssrf_rejects_credentials_in_url` | RESOLVED |
| ERR-002 | Hostile Server Test | High | `HTMLContentExtractor` did not filter hidden CSS/attribute text (`display:none`, `hidden`, `visibility:hidden`), allowing invisible adversarial injections | Added attribute inspection in `handle_starttag`/`handle_endtag` to discard hidden nodes | `test_html_extractor_discards_hidden_text_and_scripts` | RESOLVED |
| ERR-003 | Hostile Server Analysis | High | Non-textual media types (images, binary octet-streams, audio) and gzip bombs downloaded without early stream interruption | Added Content-Type whitelist and chunk-by-chunk streamed byte limit enforcement | `test_fetch_rejects_binary_media`, `test_fetch_blocks_gzip_bomb`, `test_fetch_blocks_huge_payload` | RESOLVED |
| ERR-004 | Hostile Server Analysis | Medium | Lack of `robots.txt` policy inspection before scraping paths | Added polite `is_path_allowed_by_robots` pre-flight check honoring `Disallow` rules | `test_fetch_respects_robots_txt` | RESOLVED |
| ERR-005 | Pipeline Stress Test | Medium | Missing URL count limit enforcement in `validation.py` allowing excessive URLs beyond `MAX_FILES` (5 URLs) | Added `validate_urls_metadata` in `validation.py` and enforce in `process_audit` | `test_case_12_too_many_urls_rejected` | RESOLVED |
| ERR-006 | Pipeline Stress Test | Medium | Audit timeouts returned unhandled error instead of graceful partial result with `status="incomplete"` | Wrapped claim audit loop with timeout monitor returning graceful partial findings with `status="incomplete"` and explanatory advisory banner | `test_case_15_audit_timeout_partway_incomplete_status` | RESOLVED |
| ERR-007 | Pipeline Stress Test | High | `UnboundLocalError` on `is_incomplete` variable when domain mismatch branch executed without entering `else:` claim loop | Initialized `is_incomplete = False` at top of evaluation block before branching | `test_case_1_physics_answer_maths_source_mismatch`, `test_case_2_maths_answer_physics_source_mismatch` | RESOLVED |
| ERR-008 | Targeted Suite Run | Medium | `MagicMock` responses in unit tests had `headers.get("content-type")` return mocks and non-awaitable `aclose`, causing false positive media rejections or await errors | Added type guard `isinstance(raw_ct, str)` and awaitable `safe_aclose` helper | `test_fetch_and_parse_url_mocked`, `test_audit_with_user_url` | RESOLVED |
| ERR-009 | Resiliency Stress Test | Medium | Unhandled exceptions in individual web evidence search providers crashed the entire `fetch_evidence_for_query` chain | Isolated provider queries with per-provider try/except blocks allowing fallback to subsequent providers | `test_case_9_single_provider_failure_fallback_succeeds`, `test_case_10_all_providers_failing_clean_warning` | RESOLVED |
