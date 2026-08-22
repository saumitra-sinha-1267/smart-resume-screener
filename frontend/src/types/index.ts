export type CandidateStatus =
  | 'NEW'
  | 'SCREENED'
  | 'UNDER_REVIEW'
  | 'SHORTLISTED'
  | 'INTERVIEW'
  | 'REJECTED'
  | 'HIRED';

export interface RecruiterNote {
  id: string;
  author: string;
  text: string;
  timestamp?: string;
}

export interface SkillItem {
  name: string;
  source: 'explicit_list' | 'inferred_from_bullet' | 'experience_mention';
  original_text?: string;
  quantified_evidence: boolean;
  evidence_strength?: 'STRONG' | 'MEDIUM' | 'WEAK';
}

export interface ExperienceItem {
  title: string;
  company?: string;
  start_date?: string;
  end_date?: string;
  duration_months?: number;
  bullets: string[];
  extracted_skills: string[];
}

export interface EducationItem {
  degree: string;
  institution?: string;
  year_masked: boolean;
  original_year?: string;
}

export interface ExternalLinkItem {
  url: string;
  link_type?: 'github' | 'linkedin' | 'portfolio' | 'other';
  verified: boolean | null;
  status_code?: number;
  last_active?: string;
  metadata?: Record<string, any>;
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  location?: string;
  masked_email?: string;
  masked_phone?: string;
  masked_location?: string;
}

export interface CandidateData {
  candidate_id: string;
  raw_name?: string;
  anonymized_name?: string;
  contact: ContactInfo;
  pii_stripped: boolean;
  skills: SkillItem[];
  experience: ExperienceItem[];
  education: EducationItem[];
  external_links: ExternalLinkItem[];
  total_experience_years: number;
  raw_text?: string;
  status: CandidateStatus;
  recruiter_notes: RecruiterNote[];
  tags: string[];
  created_at?: string;
}

export interface JobRequirement {
  id: string;
  text: string;
  category: string;
  weight: number;
  required: boolean;
  is_mandatory?: boolean;
}

export interface JobData {
  job_id: string;
  title: string;
  department?: string;
  seniority?: string;
  min_experience_years: number;
  required_skills: string[];
  preferred_skills: string[];
  education_requirements?: string[];
  certifications?: string[];
  domain_requirements?: string[];
  responsibilities?: string[];
  mandatory_requirements?: string[];
  preferred_requirements?: string[];
  requirements: JobRequirement[];
  raw_description: string;
  created_at?: string;
}

export interface RequirementMatch {
  requirement_id: string;
  text: string;
  category: string;
  is_mandatory: boolean;
  status: 'MATCHED' | 'PARTIAL' | 'MISSING' | 'INFERRED';
  supporting_evidence: string[];
  evidence_strength: 'STRONG' | 'MEDIUM' | 'WEAK' | 'NONE';
  reasoning: string;
}

export interface ClaimVerification {
  claim: string;
  evidence: string;
  verification_status: 'VERIFIED' | 'UNVERIFIED_PENALIZED' | 'INFERRED';
  confidence: number;
  evidence_strength: 'STRONG' | 'MEDIUM' | 'WEAK';
}

export interface SkillsMatchScore {
  score: number;
  matched: string[];
  missing: string[];
  inferred: string[];
}

export interface DimensionScore {
  score: number;
  reasoning: string;
}

export interface ScoreOutput {
  candidate_id: string;
  job_id: string;
  skills_match: SkillsMatchScore;
  experience_relevance: DimensionScore;
  education_fit: DimensionScore;
  seniority_alignment: DimensionScore;
  evidence_score?: DimensionScore;
  semantic_score?: DimensionScore;
  hard_requirements_passed: boolean;
  hard_requirements_score: number;
  soft_requirements_score: number;
  overall_score: number;
  scoring_method: 'llm' | 'calibrated_fallback';
  confidence: 'High' | 'Medium' | 'Low';
  confidence_breakdown?: Record<string, any>;
  confidence_reasons?: string[];
  flags: string[];
  summary_justification: string;
  requirement_matches?: RequirementMatch[];
  verified_claims?: ClaimVerification[];
  hallucination_guard_passed: boolean;
  hallucination_audit?: Array<{
    claimed_skill: string;
    reason: string;
    penalty_applied: number;
  }>;
  trajectory_analysis?: {
    progression_type: string;
    title_growth: string;
    stack_expansion_count: number;
    job_hopping_flag: boolean;
    average_tenure_years: number;
    is_heuristic: boolean;
    disclaimer: string;
    role_timeline?: Array<{
      role: string;
      new_skills_added: string[];
    }>;
  };
  created_at?: string;
}

export interface ScreeningResult {
  candidate: CandidateData;
  score: ScoreOutput;
  semantic_similarity_rank?: number;
  prefilter_score?: number;
}

export interface AuditLogEntry {
  log_id: string;
  event_type: string;
  candidate_id?: string;
  job_id?: string;
  actor: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface CandidateComparisonSummary {
  candidate_id: string;
  candidate_name: string;
  status: string;
  overall_score: number;
  confidence: string;
  hard_requirements_passed: boolean;
  matched_mandatory_count: number;
  total_mandatory_count: number;
  strong_evidence_count: number;
  dimension_scores: Record<string, number>;
  top_strengths: string[];
  key_gaps: string[];
}

export interface CandidateComparisonResponse {
  job_id: string;
  job_title: string;
  candidates: CandidateComparisonSummary[];
  side_by_side_matrix: Array<{
    requirement_id: string;
    text: string;
    category: string;
    is_mandatory: boolean;
    evaluations: Record<string, {
      status: string;
      evidence_strength: string;
      reasoning: string;
      evidence: string[];
    }>;
  }>;
  recommendation: string;
}
