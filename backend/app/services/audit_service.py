"""
Audit pipeline orchestrator service.
Coordinates document ingestion, chunking, claim segmentation, retrieval, and verdict mapping.
Strictly transient and in-memory; no server-side persistence.
"""
import time
from datetime import datetime, timezone
import os
import re
from typing import List, Optional, Dict
from fastapi import UploadFile

from backend.app.config import settings
from backend.app.schemas import (
    AuditResponse,
    SourceDocument,
    SourceChunk,
    ClaimFinding,
    AuditSummary,
    SourceFitSummary,
    FactualVerdict,
)
from backend.app.services.validation import (
    validate_answer,
    validate_files_metadata,
    validate_urls_metadata,
    validate_source_presence,
    validate_extracted_source_length,
)
from backend.app.services.document_parser import (
    ParsedResult,
    parse_plain_text,
    parse_pdf_bytes,
    parse_docx_bytes,
)
from backend.app.services.source_chunks import chunk_document
from backend.app.services.claim_segmenter import segment_claims
from backend.app.services.retriever import BM25Retriever
from backend.app.services.verdict_mapper import map_verdict_for_claim
from backend.app.services.summary_service import generate_audit_summary
from backend.app.services.nli_verifier import NLIVerifier
from backend.app.services.safety_flags import check_safety_concerns
from backend.app.services.source_fit import check_source_fit
from backend.app.services.web_evidence.provider_chain import web_evidence_chain
from backend.app.services.url_fetcher import fetch_and_parse_url
from backend.app.services.cost_guard import CostBudgetTracker, is_checkable_claim
from backend.app.util.hashes import generate_id, compute_sha256
from backend.app.errors import ErrorCode, SecondOpinionException

async def process_audit(
    answer: str,
    source_text: Optional[str] = None,
    files: Optional[List[UploadFile]] = None,
    urls: Optional[str] = None,
    check_source_fit_flag: Optional[bool] = None,
    min_source_fit_score: Optional[float] = None,
    enable_web_search_flag: Optional[bool] = None,
    max_audit_seconds: Optional[float] = None,
) -> AuditResponse:
    """
    Run an end-to-end source-grounded audit synchronously.
    Supports provided documents, user-submitted URLs, keyless web search fallback, and no-source web auditing.
    """
    should_enable_web_search = (
        enable_web_search_flag
        if enable_web_search_flag is not None
        else settings.WEB_EVIDENCE_ENABLED
    )

    # 1. Validation
    validate_answer(answer)
    validate_files_metadata(files)
    unique_urls = validate_urls_metadata(urls)
    validate_source_presence(source_text, files, urls=urls, allow_web_search=should_enable_web_search)

    source_documents: List[SourceDocument] = []
    all_chunks: List[SourceChunk] = []
    url_chunks_map: Dict[str, str] = {}
    seen_hashes: set = set()
    total_extracted_chars = 0
    warnings: List[str] = []
    source_name_map: Dict[str, str] = {}
    chunk_provenance_map: Dict[str, Dict[str, Any]] = {}

    # 2. Ingest pasted source text if supplied
    if source_text and source_text.strip():
        parsed_pasted = parse_plain_text(source_text, filename="pasted_source.txt")
        source_documents.append(parsed_pasted.document)
        seen_hashes.add(parsed_pasted.document.sha256)
        source_name_map[parsed_pasted.document.source_id] = parsed_pasted.document.filename
        total_extracted_chars += parsed_pasted.document.character_count

        chunks = chunk_document(parsed_pasted)
        all_chunks.extend(chunks)

    # 3. Ingest uploaded files if supplied
    if files:
        for file in files:
            if not file or not file.filename:
                continue

            content = await file.read()
            if len(content) > settings.MAX_FILE_BYTES:
                raise SecondOpinionException(
                    ErrorCode.FILE_TOO_LARGE,
                    f"File '{file.filename}' ({len(content)} bytes) exceeds the maximum allowed limit ({settings.MAX_FILE_BYTES} bytes)."
                )

            # Duplicate file check per request
            file_hash = compute_sha256(content)
            if file_hash in seen_hashes:
                warnings.append(f"Skipped duplicate file '{file.filename}' (SHA-256 match).")
                continue
            seen_hashes.add(file_hash)

            ext = os.path.splitext(file.filename)[1].lower()
            if ext == ".txt":
                text_content = content.decode("utf-8", errors="replace")
                parsed_res = parse_plain_text(text_content, filename=file.filename)
            elif ext == ".pdf":
                parsed_res = parse_pdf_bytes(content, filename=file.filename)
            elif ext == ".docx":
                parsed_res = parse_docx_bytes(content, filename=file.filename)
            else:
                raise SecondOpinionException(
                    ErrorCode.UNSUPPORTED_FILE_TYPE,
                    f"Unsupported extension for '{file.filename}'."
                )

            source_documents.append(parsed_res.document)
            source_name_map[parsed_res.document.source_id] = parsed_res.document.filename
            total_extracted_chars += parsed_res.document.character_count
            if parsed_res.document.warnings:
                warnings.extend(parsed_res.document.warnings)

            chunks = chunk_document(parsed_res)
            all_chunks.extend(chunks)

    # 3.5 Ingest web URLs if supplied
    if unique_urls:
        if urls and urls.strip():
            raw_url_count = len([u.strip() for u in re.split(r"[\n,]+", urls) if u.strip()])
            if raw_url_count > len(unique_urls):
                warnings.append("Duplicate URLs in submission were automatically deduplicated.")
        for u in unique_urls:
            doc, u_chunks = await fetch_and_parse_url(u)
            if doc.sha256 in seen_hashes:
                warnings.append(f"Skipped duplicate content from URL '{u}'.")
                continue
            seen_hashes.add(doc.sha256)
            source_documents.append(doc)
            source_name_map[doc.source_id] = doc.filename
            total_extracted_chars += doc.character_count
            all_chunks.extend(u_chunks)
            for chk in u_chunks:
                url_chunks_map[chk.chunk_id] = u
                chunk_provenance_map[chk.chunk_id] = {
                    "origin_type": "user_url",
                    "source_url": u,
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }

    # 4. Check total extracted length limit
    validate_extracted_source_length(total_extracted_chars)

    user_had_sources = len(all_chunks) > 0
    if not user_had_sources and not should_enable_web_search:
        raise SecondOpinionException(
            ErrorCode.SOURCE_EMPTY_OR_UNREADABLE,
            "Supplied sources contained no extractable textual content."
        )

    # 5. Segment answer into claims
    claims = segment_claims(answer, max_claims=settings.MAX_CLAIMS)

    # Provenance tracking map: chunk_id -> {origin_type, source_url, retrieved_at}
    chunk_provenance_map: Dict[str, dict] = {}
    now_iso = datetime.now(timezone.utc).isoformat()
    for ch in all_chunks:
        if ch.chunk_id in url_chunks_map:
            chunk_provenance_map[ch.chunk_id] = {
                "origin_type": "user_url",
                "source_url": url_chunks_map[ch.chunk_id],
                "retrieved_at": now_iso,
            }
        else:
            chunk_provenance_map[ch.chunk_id] = {
                "origin_type": "user_document",
                "source_url": None,
                "retrieved_at": None,
            }

    # 6. Source Fit Check (grades coverage before auditing; reports domain mismatch instead of false contradiction)
    should_run_source_fit = (
        check_source_fit_flag
        if check_source_fit_flag is not None
        else settings.SOURCE_FIT_ENABLED
    )
    source_fit_result: Optional[SourceFitSummary] = None

    if should_run_source_fit and source_documents and all_chunks:
        source_fit_result = check_source_fit(
            answer=answer,
            claims=claims,
            chunks=all_chunks,
            source_documents=source_documents,
            min_score_override=min_source_fit_score,
        )
        if source_fit_result.all_sources_off_topic:
            warnings.append(
                f"Source fit check: All supplied sources appear off-topic for this answer ({source_fit_result.explanation})."
            )

    # 7. Web Evidence Layer (No-source mode or off-topic fallback)
    needs_web_evidence = (
        should_enable_web_search and (
            not user_had_sources or
            (source_fit_result and source_fit_result.all_sources_off_topic)
        )
    )

    if needs_web_evidence:
        budget_tracker = CostBudgetTracker(max_queries=settings.MAX_WEB_QUERIES_PER_AUDIT)
        seen_web_urls = set()
        web_results_all = []

        for c in claims:
            # Checkability filter: do not waste queries on conversational filler or questions
            is_checkable, reason = is_checkable_claim(c.text)
            if not is_checkable:
                budget_tracker.record_skipped_uncheckable()
                continue

            if not budget_tracker.can_query():
                warnings.append(
                    f"Web search query budget reached ({budget_tracker.max_queries} queries executed). Additional claims evaluated locally."
                )
                break

            budget_tracker.record_query()
            res_list = await web_evidence_chain.fetch_evidence_for_query(c.text, max_results=2)
            for r in res_list:
                if r.url not in seen_web_urls:
                    seen_web_urls.add(r.url)
                    web_results_all.append(r)

        if web_results_all:
            web_docs, web_chunks, res_map = web_evidence_chain.convert_results_to_sources(web_results_all)
            source_documents.extend(web_docs)
            all_chunks.extend(web_chunks)
            for ch in web_chunks:
                res_item = res_map.get(ch.chunk_id)
                if res_item:
                    source_name_map[ch.source_id] = res_item.source_name
                    chunk_provenance_map[ch.chunk_id] = {
                        "origin_type": res_item.origin_type,
                        "source_url": res_item.url,
                        "retrieved_at": res_item.retrieved_at,
                    }
            warnings.append(f"Retrieved {len(web_docs)} web evidence passages for grounding.")

    if not all_chunks:
        raise SecondOpinionException(
            ErrorCode.SOURCE_EMPTY_OR_UNREADABLE,
            "No local sources provided and web search returned no matching evidence."
        )

    # Resolve source_mode
    has_web_sources = any(p.get("origin_type") != "user_document" for p in chunk_provenance_map.values())
    if has_web_sources and not user_had_sources:
        source_mode = "web_search"
    elif has_web_sources and user_had_sources:
        source_mode = "mixed"
    else:
        source_mode = "provided_sources"

    findings: List[ClaimFinding] = []
    is_incomplete = False

    # If all sources are off-topic AND no web search was executed/succeeded, prevent false contradictions
    if source_fit_result and source_fit_result.all_sources_off_topic and not has_web_sources:
        for claim in claims:
            safety_concerns = check_safety_concerns(claim.text)
            finding = ClaimFinding(
                claim_id=claim.claim_id,
                claim_text=claim.text,
                start_char=claim.start_char,
                end_char=claim.end_char,
                verdict=FactualVerdict.NOT_ESTABLISHED_BY_SOURCE,
                explanation=f"Source does not cover this topic: {source_fit_result.explanation} Unverified due to domain mismatch, not false.",
                evidence=[],
                logic_concerns=[],
                safety_concerns=safety_concerns,
                review_priority="high",
                evidence_strength=0.0,
                model_details=None,
                warnings=["Source domain mismatch: all sources off-topic."],
                independent_sources_agreeing=0,
            )
            findings.append(finding)
    else:
        # 8. BM25 Retrieval and Verdict Mapping with provenance
        retriever = BM25Retriever(all_chunks)
        nli_verifier = NLIVerifier.get_instance() if settings.MODEL_ENABLED else None

        start_time = time.monotonic()
        is_incomplete = False
        for claim in claims:
            if max_audit_seconds and (time.monotonic() - start_time) > max_audit_seconds:
                warnings.append(
                    f"Audit execution reached time limit ({max_audit_seconds}s) after evaluating {len(findings)} of {len(claims)} claims. Returning partial results."
                )
                is_incomplete = True
                break

            candidates = retriever.retrieve_candidates(
                query=claim.text,
                source_name_map=source_name_map,
                chunk_provenance_map=chunk_provenance_map,
                top_k=3
            )
            finding = map_verdict_for_claim(
                claim=claim,
                candidate_evidence=candidates,
                nli_verifier=nli_verifier
            )
            findings.append(finding)

    # 9. Aggregate Summary
    summary = generate_audit_summary(findings)

    audit_id = generate_id("audit")
    created_at = datetime.now(timezone.utc).isoformat()

    engine_metadata = {
        "verifier_mode": "rules_and_model" if (settings.MODEL_ENABLED and NLIVerifier.get_instance().is_loaded) else "rules_only",
        "retrieval_engine": "BM25Plus",
        "total_source_chunks": len(all_chunks),
        "total_sources": len(source_documents),
        "source_fit_checked": source_fit_result is not None,
        "web_search_enabled": should_enable_web_search,
    }

    return AuditResponse(
        audit_id=audit_id,
        status="incomplete" if is_incomplete else "completed",
        source_mode=source_mode,
        original_answer=answer,
        sources=source_documents,
        findings=findings,
        summary=summary,
        warnings=warnings,
        engine_metadata=engine_metadata,
        created_at=created_at,
        source_fit=source_fit_result,
    )

def generate_markdown_report(audit: AuditResponse) -> str:
    """
    Generate a clean, professional, human-readable Markdown audit report.
    Ready for download or saving.
    """
    lines = [
        f"# Second Opinion — Audit Report",
        f"**Audit ID:** `{audit.audit_id}`  ",
        f"**Generated:** {audit.created_at}  ",
        f"**Assessment:** {audit.summary.assessment}  ",
        "",
        "## Executive Summary",
        f"- **Review Recommendation:** {audit.summary.review_recommendation}",
        f"- **Total Claims Audited:** {audit.summary.total_claims}",
        f"- **Supported by Sources:** {audit.summary.supported_claims}",
        f"- **Contradicted by Sources:** {audit.summary.contradicted_claims}",
        f"- **Not Established by Sources:** {audit.summary.not_established_claims}",
        f"- **Ambiguous / Conflicting Evidence:** {audit.summary.ambiguous_claims}",
        "",
    ]

    if audit.source_fit:
        lines.append("## Source Fit Assessment")
        lines.append(f"- **Overall Alignment:** {audit.source_fit.overall_fit.value}")
        lines.append(f"- **Average Fit Score:** {audit.source_fit.average_fit_score:.0%}")
        lines.append(f"- **Coverage Status:** {audit.source_fit.explanation}")
        lines.append("")
        lines.append("### Source Document Details")
        for doc in audit.source_fit.documents:
            lines.append(f"- **{doc.filename}**: {doc.fit_level.value} ({doc.fit_score:.0%})")
            lines.append(f"  *{doc.reason}*")
        lines.append("")

    if audit.warnings:
        lines.append("## System Warnings")
        for w in audit.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    lines.append("## Claim-by-Claim Findings")
    for idx, finding in enumerate(audit.findings, start=1):
        lines.append(f"### Claim {idx} [{finding.verdict.value}]")
        lines.append(f"> \"{finding.claim_text}\"")
        lines.append(f"**Explanation:** {finding.explanation}  ")
        lines.append(f"**Review Priority:** {finding.review_priority.upper()}  ")

        if finding.evidence:
            lines.append("**Evidence Passages:**")
            for evi in finding.evidence:
                page_info = f" (Page {evi.page_number})" if evi.page_number else ""
                lines.append(f"- *From {evi.source_name}{page_info} (Rank {evi.retrieval_rank}):*")
                lines.append(f"  > \"{evi.quote.strip()}\"")

        if finding.safety_concerns:
            lines.append("**Advisory Flags:**")
            for sc in finding.safety_concerns:
                lines.append(f"- 🛡️ {sc}")

        lines.append("")

    lines.append("---")
    lines.append("*Disclaimer: Second Opinion is an evidence-grounding audit tool, not a certified legal, medical, or financial decision system.*")
    return "\n".join(lines)

