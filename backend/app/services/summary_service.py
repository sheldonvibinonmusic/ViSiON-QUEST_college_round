"""
Audit summary aggregation service.
Computes transparent counts and review status without calculating ungrounded universal percentages.
"""
from typing import List
from backend.app.schemas import ClaimFinding, AuditSummary, FactualVerdict

def generate_audit_summary(findings: List[ClaimFinding]) -> AuditSummary:
    """
    Aggregate claim-level findings into a transparent summary.
    Avoids single-percentage masking; highlights severe issues directly.
    """
    total = len(findings)
    supported = sum(1 for f in findings if f.verdict == FactualVerdict.SUPPORTED_BY_SOURCE)
    contradicted = sum(1 for f in findings if f.verdict == FactualVerdict.CONTRADICTED_BY_SOURCE)
    not_established = sum(1 for f in findings if f.verdict == FactualVerdict.NOT_ESTABLISHED_BY_SOURCE)
    ambiguous = sum(1 for f in findings if f.verdict == FactualVerdict.AMBIGUOUS_OR_CONFLICTING)

    logic_concerns_count = sum(len(f.logic_concerns) for f in findings)
    safety_concerns_count = sum(len(f.safety_concerns) for f in findings)

    # Determine overall assessment and review recommendation
    if contradicted > 0:
        assessment = "Contradictions Detected"
        recommendation = "High Priority: Answer contains claims directly contradicted by reference sources. Review flagged passages before relying on this text."
    elif ambiguous > 0 or not_established > 0:
        assessment = "Needs Source Verification"
        recommendation = "Medium Priority: Answer contains unverified or ambiguous claims that could not be confirmed in the provided source documents."
    elif total > 0 and supported == total:
        assessment = "Supported by Provided Sources"
        recommendation = "Low Priority: All identified claims are supported by the provided reference passages."
    else:
        assessment = "No Auditable Claims"
        recommendation = "No auditable claims were extracted from the answer."

    summary_text = (
        f"Audited {total} claims: {supported} supported, {contradicted} contradicted, "
        f"{not_established} not established by sources, {ambiguous} ambiguous/conflicting."
    )
    if safety_concerns_count > 0:
        summary_text += f" {safety_concerns_count} high-stakes domain advisory flags raised."

    return AuditSummary(
        assessment=assessment,
        review_recommendation=recommendation,
        total_claims=total,
        supported_claims=supported,
        contradicted_claims=contradicted,
        not_established_claims=not_established,
        ambiguous_claims=ambiguous,
        logic_concerns_count=logic_concerns_count,
        safety_concerns_count=safety_concerns_count,
        summary_text=summary_text,
    )
