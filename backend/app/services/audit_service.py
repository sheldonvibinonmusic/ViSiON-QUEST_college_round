"""
Audit pipeline orchestrator service.
Coordinates document ingestion, chunking, claim segmentation, retrieval, and verdict mapping.
Strictly transient and in-memory; no server-side persistence.
"""
from datetime import datetime, timezone
import os
from typing import List, Optional, Dict
from fastapi import UploadFile

from backend.app.config import settings
from backend.app.schemas import (
    AuditResponse,
    SourceDocument,
    SourceChunk,
    ClaimFinding,
    AuditSummary,
)
from backend.app.services.validation import (
    validate_answer,
    validate_files_metadata,
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
from backend.app.util.hashes import generate_id, compute_sha256
from backend.app.errors import ErrorCode, SecondOpinionException

async def process_audit(
    answer: str,
    source_text: Optional[str] = None,
    files: Optional[List[UploadFile]] = None
) -> AuditResponse:
    """
    Run an end-to-end source-grounded audit synchronously.
    """
    # 1. Validation
    validate_answer(answer)
    validate_files_metadata(files)
    validate_source_presence(source_text, files)

    source_documents: List[SourceDocument] = []
    all_chunks: List[SourceChunk] = []
    seen_hashes: set = set()
    total_extracted_chars = 0
    warnings: List[str] = []
    source_name_map: Dict[str, str] = {}

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

    # 4. Check total extracted length limit
    validate_extracted_source_length(total_extracted_chars)

    if not all_chunks:
        raise SecondOpinionException(
            ErrorCode.SOURCE_EMPTY_OR_UNREADABLE,
            "Supplied sources contained no extractable textual content."
        )

    # 5. Segment answer into claims
    claims = segment_claims(answer, max_claims=settings.MAX_CLAIMS)

    # 6. BM25 Retrieval and Verdict Mapping
    retriever = BM25Retriever(all_chunks)
    nli_verifier = NLIVerifier.get_instance() if settings.MODEL_ENABLED else None

    findings: List[ClaimFinding] = []
    for claim in claims:
        candidates = retriever.retrieve_candidates(
            query=claim.text,
            source_name_map=source_name_map,
            top_k=3
        )
        finding = map_verdict_for_claim(
            claim=claim,
            candidate_evidence=candidates,
            nli_verifier=nli_verifier
        )
        findings.append(finding)

    # 7. Aggregate Summary
    summary = generate_audit_summary(findings)

    audit_id = generate_id("audit")
    created_at = datetime.now(timezone.utc).isoformat()

    engine_metadata = {
        "verifier_mode": "rules_and_model" if (nli_verifier and nli_verifier.is_loaded) else "rules_only",
        "retrieval_engine": "BM25Plus",
        "total_source_chunks": len(all_chunks),
        "total_sources": len(source_documents)
    }

    return AuditResponse(
        audit_id=audit_id,
        status="completed",
        source_mode="provided_sources",
        original_answer=answer,
        sources=source_documents,
        findings=findings,
        summary=summary,
        warnings=warnings,
        engine_metadata=engine_metadata,
        created_at=created_at
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
