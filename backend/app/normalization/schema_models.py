import uuid
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

# ==============================================================================
# SKILLS & EVIDENCE SCHEMAS
# ==============================================================================
class SkillItem(BaseModel):
    name: str
    source: str = Field(default="explicit_list", description="explicit_list | inferred_from_bullet | experience_mention")
    original_text: Optional[str] = None
    quantified_evidence: bool = False
    evidence_strength: Literal["STRONG", "MEDIUM", "WEAK"] = "MEDIUM"

class ExperienceItem(BaseModel):
    title: str
    company: Optional[str] = None
    start_date: Optional[str] = None  # YYYY-MM
    end_date: Optional[str] = None    # YYYY-MM or 'Present'
    duration_months: Optional[int] = 0
    bullets: List[str] = []
    extracted_skills: List[str] = []

class EducationItem(BaseModel):
    degree: str
    institution: Optional[str] = None
    year_masked: bool = True
    original_year: Optional[str] = None

class ExternalLinkItem(BaseModel):
    url: str
    link_type: Optional[str] = "other"  # github | linkedin | portfolio | other
    verified: Optional[bool] = False
    status_code: Optional[int] = None
    last_active: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    masked_email: Optional[str] = None
    masked_phone: Optional[str] = None
    masked_location: Optional[str] = None

# ==============================================================================
# CANDIDATE WORKFLOW SCHEMAS
# ==============================================================================
CandidateStatus = Literal[
    "NEW",
    "SCREENED",
    "UNDER_REVIEW",
    "SHORTLISTED",
    "INTERVIEW",
    "REJECTED",
    "HIRED"
]

class RecruiterNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    author: str = "Recruiter"
    text: str
    timestamp: Optional[str] = None

class CandidateData(BaseModel):
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_name: Optional[str] = None
    anonymized_name: Optional[str] = "Candidate"
    contact: ContactInfo = Field(default_factory=ContactInfo)
    pii_stripped: bool = True
    skills: List[SkillItem] = []
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    external_links: List[ExternalLinkItem] = []
    total_experience_years: float = 0.0
    raw_text: Optional[str] = None
    status: CandidateStatus = "NEW"
    recruiter_notes: List[RecruiterNote] = []
    tags: List[str] = []
    created_at: Optional[str] = None

# ==============================================================================
# JOB & REQUIREMENTS SCHEMAS
# ==============================================================================
class JobRequirement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    category: str = "skill"  # skill | experience | education | certification | domain | leadership | responsibility
    weight: float = 1.0
    required: bool = True
    is_mandatory: bool = True

class JobData(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    department: Optional[str] = "Engineering"
    seniority: Optional[str] = "Mid-Senior"
    min_experience_years: float = 0.0
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_requirements: List[str] = []
    certifications: List[str] = []
    domain_requirements: List[str] = []
    responsibilities: List[str] = []
    mandatory_requirements: List[str] = []
    preferred_requirements: List[str] = []
    requirements: List[JobRequirement] = []
    raw_description: str
    created_at: Optional[str] = None

# ==============================================================================
# REQUIREMENT MATCHING & EVIDENCE AUDIT SCHEMAS
# ==============================================================================
class RequirementMatch(BaseModel):
    requirement_id: str
    text: str
    category: str
    is_mandatory: bool
    status: Literal["MATCHED", "PARTIAL", "MISSING", "INFERRED"]
    supporting_evidence: List[str] = []
    evidence_strength: Literal["STRONG", "MEDIUM", "WEAK", "NONE"] = "NONE"
    reasoning: str

class ClaimVerification(BaseModel):
    claim: str
    evidence: str
    verification_status: Literal["VERIFIED", "UNVERIFIED_PENALIZED", "INFERRED", "UNCONFIRMED"]
    confidence: float = 1.0
    evidence_strength: Literal["STRONG", "MEDIUM", "WEAK", "NONE"] = "MEDIUM"

class SkillsMatchScore(BaseModel):
    score: float = Field(ge=0, le=10)
    matched: List[str] = []
    missing: List[str] = []
    inferred: List[str] = []

class DimensionScore(BaseModel):
    score: float = Field(ge=0, le=10)
    reasoning: str

class ScoreOutput(BaseModel):
    candidate_id: str
    job_id: str
    skills_match: SkillsMatchScore
    experience_relevance: DimensionScore
    education_fit: DimensionScore
    seniority_alignment: DimensionScore
    evidence_score: Optional[DimensionScore] = None
    semantic_score: Optional[DimensionScore] = None
    hard_requirements_passed: bool = True
    hard_requirements_score: float = 0.0
    soft_requirements_score: float = 0.0
    overall_score: float = Field(ge=0, le=10)
    scoring_method: Literal["llm", "calibrated_fallback"] = "calibrated_fallback"
    confidence: str = Field(description="High | Medium | Low")
    confidence_breakdown: Optional[Dict[str, Any]] = None
    confidence_reasons: List[str] = []
    flags: List[str] = []
    summary_justification: str
    requirement_matches: List[RequirementMatch] = []
    verified_claims: List[ClaimVerification] = []
    hallucination_guard_passed: bool = True
    hallucination_audit: Optional[List[Dict[str, Any]]] = None
    trajectory_analysis: Optional[Dict[str, Any]] = None
    scoring_weights_used: Optional[Dict[str, float]] = None
    created_at: Optional[str] = None

class ScreeningResult(BaseModel):
    candidate: CandidateData
    score: ScoreOutput
    semantic_similarity_rank: Optional[int] = None
    prefilter_score: Optional[float] = None

# ==============================================================================
# AUDIT LOG & COMPARISON SCHEMAS
# ==============================================================================
class AuditLogEntry(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    actor: str = "system"
    details: Dict[str, Any] = {}
    timestamp: str

class CandidateComparisonRequest(BaseModel):
    candidate_ids: List[str]
    job_id: str

class CandidateComparisonSummary(BaseModel):
    candidate_id: str
    candidate_name: str
    status: str
    overall_score: float
    confidence: str
    hard_requirements_passed: bool
    matched_mandatory_count: int
    total_mandatory_count: int
    strong_evidence_count: int
    dimension_scores: Dict[str, float]
    top_strengths: List[str]
    key_gaps: List[str]

class CandidateComparisonResponse(BaseModel):
    job_id: str
    job_title: str
    candidates: List[CandidateComparisonSummary]
    side_by_side_matrix: List[Dict[str, Any]]
    recommendation: str
