"""
Pydantic v2 schemas and canonical data models for Second Opinion.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FactualVerdict(str, Enum):
    SUPPORTED_BY_SOURCE = "SUPPORTED_BY_SOURCE"
    CONTRADICTED_BY_SOURCE = "CONTRADICTED_BY_SOURCE"
    NOT_ESTABLISHED_BY_SOURCE = "NOT_ESTABLISHED_BY_SOURCE"
    AMBIGUOUS_OR_CONFLICTING = "AMBIGUOUS_OR_CONFLICTING"

class VerifierMode(str, Enum):
    RULES_AND_MODEL = "rules_and_model"
    RULES_ONLY = "rules_only"

class SystemLimits(BaseModel):
    max_answer_chars: int
    max_source_chars: int
    max_files: int
    max_file_bytes: int
    max_claims: int

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    verifier_mode: VerifierMode = VerifierMode.RULES_ONLY
    model_loaded: bool = False
    model_id: str
    supported_file_types: List[str]
    limits: SystemLimits

class SourceDocument(BaseModel):
    source_id: str
    filename: str
    media_type: str
    sha256: str
    character_count: int
    page_count: Optional[int] = None
    extraction_status: str = "success"
    warnings: List[str] = Field(default_factory=list)

class SourceChunk(BaseModel):
    chunk_id: str
    source_id: str
    text: str
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    section: Optional[str] = None
    retrieval_score: Optional[float] = None

class Claim(BaseModel):
    claim_id: str
    text: str
    start_char: int
    end_char: int
    parent_sentence: Optional[str] = None
    compound_claim_review: bool = False
    flags: List[str] = Field(default_factory=list)

class EvidenceReference(BaseModel):
    """
    Substantive evidence quote retrieved from a source document or web origin.
    Preserves exact character offsets and origin provenance.
    """
    evidence_id: str
    source_id: str
    source_name: str
    quote: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    start_char: int
    end_char: int
    relation: str
    retrieval_rank: int
    origin_type: str = Field(
        default="user_document",
        description="Origin provenance: 'user_document', 'user_url', 'wikipedia', 'scholarly_arxiv', 'scholarly_crossref', or 'web_search'"
    )
    source_url: Optional[str] = Field(default=None, description="External origin URL if source was retrieved online")
    retrieved_at: Optional[str] = Field(default=None, description="UTC timestamp of retrieval")
    citation_verified: Optional[bool] = Field(default=None, description="Whether citation covers substantive claim content")

class ClaimFinding(BaseModel):
    """
    Forensic evaluation finding for an individual decomposed claim.
    """
    claim_id: str
    claim_text: str
    start_char: int
    end_char: int
    verdict: FactualVerdict
    explanation: str
    evidence: List[EvidenceReference] = Field(default_factory=list)
    logic_concerns: List[str] = Field(default_factory=list)
    safety_concerns: List[str] = Field(default_factory=list)
    review_priority: str = Field(default="low", description="Triage priority: 'low', 'medium', or 'high'")
    evidence_strength: float = 0.0
    model_details: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
    independent_sources_agreeing: int = Field(default=1, description="Number of distinct sources corroborating the finding")
    checks: List[Dict[str, Any]] = Field(default_factory=list, description="Granular verification checks executed")
    verdict_reason: Optional[str] = Field(default=None, description="One-line human explanation of the primary factor driving the verdict")

class AuditSummary(BaseModel):
    assessment: str
    review_recommendation: str
    total_claims: int = 0
    supported_claims: int = 0
    contradicted_claims: int = 0
    not_established_claims: int = 0
    ambiguous_claims: int = 0
    logic_concerns_count: int = 0
    safety_concerns_count: int = 0
    summary_text: str = ""

class SourceFitLevel(str, Enum):
    RELEVANT = "RELEVANT"
    PARTIALLY_RELEVANT = "PARTIALLY_RELEVANT"
    OFF_TOPIC = "OFF_TOPIC"

class SourceFitDocument(BaseModel):
    source_id: str
    filename: str
    fit_level: SourceFitLevel
    fit_score: float
    matched_terms: List[str] = Field(default_factory=list)
    missing_topics: List[str] = Field(default_factory=list)
    reason: str

class SourceFitSummary(BaseModel):
    overall_fit: SourceFitLevel
    average_fit_score: float
    all_sources_off_topic: bool
    documents: List[SourceFitDocument] = Field(default_factory=list)
    explanation: str

class AuditResponse(BaseModel):
    audit_id: str
    status: str = "completed"
    source_mode: str = "provided_sources"
    original_answer: str
    sources: List[SourceDocument] = Field(default_factory=list)
    findings: List[ClaimFinding] = Field(default_factory=list)
    summary: AuditSummary
    warnings: List[str] = Field(default_factory=list)
    engine_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    source_fit: Optional[SourceFitSummary] = None
    truncated: Optional[bool] = Field(default=None, description="Whether input sources exceeded limits and were truncated")
    original_size: Optional[int] = Field(default=None, description="Original source character count before truncation")
    kept_size: Optional[int] = Field(default=None, description="Kept source character count after truncation")
    incomplete: Optional[bool] = Field(default=None, description="Whether audit was truncated by deadline timeout")
    pages_crawled: Optional[int] = Field(default=None, description="Number of subpages crawled for URL sources")


