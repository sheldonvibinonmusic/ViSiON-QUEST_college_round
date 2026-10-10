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

class ClaimFinding(BaseModel):
    claim_id: str
    claim_text: str
    start_char: int
    end_char: int
    verdict: FactualVerdict
    explanation: str
    evidence: List[EvidenceReference] = Field(default_factory=list)
    logic_concerns: List[str] = Field(default_factory=list)
    safety_concerns: List[str] = Field(default_factory=list)
    review_priority: str = "low"  # low, medium, high
    evidence_strength: float = 0.0
    model_details: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)

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
