import sqlite3
import json
import os
import re
import glob
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.normalization.schema_models import (
    CandidateData, JobData, ScoreOutput, RecruiterNote,
    CandidateComparisonSummary, CandidateComparisonResponse
)

_initialized_dbs = set()

def _init_tables_internal(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        candidate_id TEXT PRIMARY KEY,
        raw_name TEXT,
        anonymized_name TEXT,
        status TEXT DEFAULT 'NEW',
        total_experience_years REAL,
        skills_count INTEGER,
        data_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        department TEXT,
        min_experience_years REAL,
        data_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        job_id TEXT NOT NULL,
        overall_score REAL NOT NULL,
        confidence TEXT NOT NULL,
        score_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(candidate_id, job_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        upload_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        candidate_id TEXT,
        file_size INTEGER,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        candidate_id TEXT,
        job_id TEXT,
        actor TEXT NOT NULL,
        details_json TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)
    cursor.execute("PRAGMA table_info(candidates)")
    c_cols = [row["name"] for row in cursor.fetchall()]
    if "status" not in c_cols:
        cursor.execute("ALTER TABLE candidates ADD COLUMN status TEXT DEFAULT 'NEW'")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenings_job ON screenings(job_id, overall_score DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_candidates_created ON candidates(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_candidate ON audit_logs(candidate_id, timestamp DESC);")
    conn.commit()

def get_connection():
    conn = sqlite3.connect(settings.DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    if settings.DB_PATH not in _initialized_dbs:
        _init_tables_internal(conn)
        _initialized_dbs.add(settings.DB_PATH)
    return conn

def init_db():
    conn = sqlite3.connect(settings.DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    _init_tables_internal(conn)
    _initialized_dbs.add(settings.DB_PATH)
    conn.close()

def save_candidate(candidate: CandidateData) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    if not candidate.created_at:
        candidate.created_at = now

    cursor.execute("""
    INSERT OR REPLACE INTO candidates (
        candidate_id, raw_name, anonymized_name, status, total_experience_years, skills_count, data_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate.candidate_id,
        candidate.raw_name,
        candidate.anonymized_name,
        candidate.status,
        candidate.total_experience_years,
        len(candidate.skills),
        json.dumps(candidate.model_dump(), ensure_ascii=False),
        candidate.created_at
    ))
    conn.commit()
    conn.close()

def update_candidate_status(candidate_id: str, new_status: str) -> Optional[CandidateData]:
    cand = get_candidate(candidate_id)
    if not cand:
        return None
    cand.status = new_status
    save_candidate(cand)
    return cand

def add_recruiter_note(candidate_id: str, text: str, author: str = "Recruiter") -> Optional[CandidateData]:
    cand = get_candidate(candidate_id)
    if not cand:
        return None
    note = RecruiterNote(
        author=author,
        text=text,
        timestamp=datetime.utcnow().isoformat()
    )
    cand.recruiter_notes.append(note)
    save_candidate(cand)
    return cand

def get_candidate(candidate_id: str) -> Optional[CandidateData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM candidates WHERE candidate_id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return CandidateData(**json.loads(row["data_json"]))
    return None

def list_candidates() -> List[CandidateData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM candidates ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [CandidateData(**json.loads(r["data_json"])) for r in rows]

def delete_candidate(candidate_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT file_path FROM uploads WHERE candidate_id = ?", (candidate_id,))
    upload_rows = cursor.fetchall()
    for u in upload_rows:
        f_path = u["file_path"]
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
            except Exception:
                pass

    cursor.execute("DELETE FROM uploads WHERE candidate_id = ?", (candidate_id,))
    cursor.execute("DELETE FROM screenings WHERE candidate_id = ?", (candidate_id,))
    cursor.execute("DELETE FROM candidates WHERE candidate_id = ?", (candidate_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def delete_all_candidates() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM uploads")
    for u in cursor.fetchall():
        if os.path.exists(u["file_path"]):
            try:
                os.remove(u["file_path"])
            except Exception:
                pass
    for f in glob.glob(os.path.join(settings.UPLOADS_DIR, "*")):
        try:
            os.remove(f)
        except Exception:
            pass

    cursor.execute("DELETE FROM uploads")
    cursor.execute("DELETE FROM screenings")
    cursor.execute("DELETE FROM candidates")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def save_job(job: JobData) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    if not job.created_at:
        job.created_at = now

    cursor.execute("""
    INSERT OR REPLACE INTO jobs (
        job_id, title, department, min_experience_years, data_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job.job_id,
        job.title,
        job.department,
        job.min_experience_years,
        json.dumps(job.model_dump(), ensure_ascii=False),
        job.created_at
    ))
    conn.commit()
    conn.close()

def get_job(job_id: str) -> Optional[JobData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return JobData(**json.loads(row["data_json"]))
    return None

def list_jobs() -> List[JobData]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM jobs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [JobData(**json.loads(r["data_json"])) for r in rows]

def save_screening(score: ScoreOutput) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    if not score.created_at:
        score.created_at = now

    cursor.execute("""
    INSERT OR REPLACE INTO screenings (
        candidate_id, job_id, overall_score, confidence, score_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        score.candidate_id,
        score.job_id,
        score.overall_score,
        score.confidence,
        json.dumps(score.model_dump(), ensure_ascii=False),
        score.created_at
    ))
    conn.commit()
    conn.close()

def get_screenings_for_job(job_id: str) -> List[ScoreOutput]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT score_json FROM screenings 
    WHERE job_id = ? 
    ORDER BY overall_score DESC
    """, (job_id,))
    rows = cursor.fetchall()
    conn.close()
    return [ScoreOutput(**json.loads(r["score_json"])) for r in rows]

def get_screening(candidate_id: str, job_id: str) -> Optional[ScoreOutput]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT score_json FROM screenings 
    WHERE candidate_id = ? AND job_id = ?
    """, (candidate_id, job_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return ScoreOutput(**json.loads(row["score_json"]))
    return None

def compare_candidates_for_job(candidate_ids: List[str], job_id: str) -> CandidateComparisonResponse:
    """Generates a structured side-by-side evaluation comparison across multiple candidates."""
    job = get_job(job_id)
    if not job:
        raise ValueError(f"Job '{job_id}' not found")

    summaries: List[CandidateComparisonSummary] = []
    matrix_map: Dict[str, Dict[str, Any]] = {} # req_id -> { "text": ..., "evaluations": { cand_id: match_obj } }

    for req in job.requirements:
        matrix_map[req.id] = {
            "requirement_id": req.id,
            "text": req.text,
            "category": req.category,
            "is_mandatory": req.is_mandatory or req.required,
            "evaluations": {}
        }

    for c_id in candidate_ids:
        cand = get_candidate(c_id)
        if not cand:
            continue
        sc = get_screening(c_id, job_id)

        mand_matches = [r for r in (sc.requirement_matches if sc else []) if r.is_mandatory]
        mand_matched_count = len([r for r in mand_matches if r.status in ["MATCHED", "INFERRED"]])
        strong_ev_count = sum(1 for s in cand.skills if s.evidence_strength == "STRONG" or s.quantified_evidence)

        # Build strengths and gaps dynamically from requirement matrix
        strengths = []
        gaps = []
        if sc:
            req_matches = sc.requirement_matches or []
            mand_skills = [r for r in req_matches if r.category == "skill" and r.is_mandatory]
            matched_mand = [r for r in mand_skills if r.status in ["MATCHED", "INFERRED"]]
            pref_skills = [r for r in req_matches if r.category == "skill" and not r.is_mandatory]
            matched_pref = [r for r in pref_skills if r.status in ["MATCHED", "INFERRED"]]

            if mand_skills:
                pref_names = [re.sub(r"^(?:Demonstrated hands-on expertise with|Hands-on expertise in|Experience or familiarity with|Familiarity with|Expertise in)\s+", "", p.text, flags=re.IGNORECASE).strip() for p in matched_pref]
                if pref_names:
                    strengths.append(f"Matches {len(matched_mand)} of {len(mand_skills)} mandatory skills, with additional experience in {' and '.join(pref_names[:2])}")
                else:
                    strengths.append(f"Matches {len(matched_mand)} of {len(mand_skills)} mandatory skills")
            elif sc.skills_match.matched:
                strengths.append(f"Strong match in {', '.join(sc.skills_match.matched[:3])}")

            if sc.experience_relevance.score >= 8.0:
                strengths.append(f"{cand.total_experience_years} years verified experience")
            if strong_ev_count >= 2:
                strengths.append(f"{strong_ev_count} quantified outcome metrics")

            missing_mand = [r for r in req_matches if r.is_mandatory and r.status == "MISSING"]
            if missing_mand:
                clean_names = [re.sub(r"^(?:Demonstrated hands-on expertise with|Hands-on expertise in|Experience or familiarity with|Familiarity with|Expertise in)\s+", "", m.text, flags=re.IGNORECASE).strip() for m in missing_mand]
                if len(clean_names) == 1:
                    gaps.append(f"One mandatory skill is not evidenced: {clean_names[0]}")
                else:
                    gaps.append(f"{len(clean_names)} mandatory skills are not evidenced: {', '.join(clean_names)}")
            elif sc.skills_match.missing:
                gaps.append(f"Missing skills: {', '.join(sc.skills_match.missing[:2])}")

        dim_scores = {
            "skills": sc.skills_match.score if sc else 0.0,
            "experience": sc.experience_relevance.score if sc else 0.0,
            "evidence": sc.evidence_score.score if sc and sc.evidence_score else 0.0,
            "seniority": sc.seniority_alignment.score if sc else 0.0,
            "education": sc.education_fit.score if sc else 0.0
        }

        summaries.append(CandidateComparisonSummary(
            candidate_id=cand.candidate_id,
            candidate_name=cand.anonymized_name or f"Candidate #{cand.candidate_id[:6]}",
            status=cand.status,
            overall_score=sc.overall_score if sc else 0.0,
            confidence=sc.confidence if sc else "Low",
            hard_requirements_passed=sc.hard_requirements_passed if sc else False,
            matched_mandatory_count=mand_matched_count,
            total_mandatory_count=len(mand_matches),
            strong_evidence_count=strong_ev_count,
            dimension_scores=dim_scores,
            top_strengths=strengths[:3],
            key_gaps=gaps[:3]
        ))

        # Populate matrix
        if sc and sc.requirement_matches:
            for rm in sc.requirement_matches:
                if rm.requirement_id in matrix_map:
                    matrix_map[rm.requirement_id]["evaluations"][cand.candidate_id] = {
                        "status": rm.status,
                        "evidence_strength": rm.evidence_strength,
                        "reasoning": rm.reasoning,
                        "evidence": rm.supporting_evidence
                    }

    # Sort candidates by overall score descending
    summaries.sort(key=lambda s: s.overall_score, reverse=True)

    recommendation = ""
    if summaries:
        top_cand = summaries[0]
        recommendation = f"Top recommended candidate is {top_cand.candidate_name} with an overall score of {top_cand.overall_score}/10 ({top_cand.confidence} confidence)."
        if not top_cand.hard_requirements_passed:
            recommendation += " Note: candidate has partial gaps on hard requirements requiring manual interview probing."
    else:
        recommendation = "No candidates evaluated yet for this role."

    return CandidateComparisonResponse(
        job_id=job.job_id,
        job_title=job.title,
        candidates=summaries,
        side_by_side_matrix=list(matrix_map.values()),
        recommendation=recommendation
    )

# Initialize on load
init_db()
