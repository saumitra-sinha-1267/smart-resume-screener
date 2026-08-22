import os
import re
import uuid
import shutil
import asyncio
import logging
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, status, Body
from app.core.config import settings
from app.core import database
from app.core.audit import record_audit_event
from app.normalization.schema_models import (
    CandidateData, CandidateStatus, RecruiterNote,
    CandidateComparisonRequest, CandidateComparisonResponse
)
from app.normalization.pii_stripper import anonymize_candidate
from app.extraction.pdf_extractor import extract_raw_text_from_pdf, parse_resume_to_candidate
from app.evidence.metric_detector import enrich_candidate_with_evidence
from app.evidence.link_checker import verify_candidate_links

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["Candidates"])

# Security Constraints
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "application/octet-stream"
}
EXTRACTION_TIMEOUT_SECONDS = 15.0

class StatusUpdateRequest(BaseModel):
    status: CandidateStatus

class RecruiterNoteRequest(BaseModel):
    text: str
    author: Optional[str] = "Recruiter"

def sanitize_filename(filename: str) -> str:
    if not filename:
        return "resume_upload.pdf"
    clean_name = os.path.basename(filename.replace("\\", "/"))
    clean_name = clean_name.replace("..", "")
    clean_name = re.sub(r"[^a-zA-Z0-9._\- ]", "_", clean_name).strip()
    if not clean_name:
        clean_name = "resume_upload.pdf"
    return clean_name

@router.get("", response_model=List[CandidateData])
def list_candidates(anonymized: bool = Query(True, description="Toggle PII masking")):
    candidates = database.list_candidates()
    return [anonymize_candidate(c, strip=anonymized) for c in candidates]

@router.get("/{candidate_id}", response_model=CandidateData)
def get_candidate(candidate_id: str, anonymized: bool = Query(True, description="Toggle PII masking")):
    cand = database.get_candidate(candidate_id)
    if not cand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return anonymize_candidate(cand, strip=anonymized)

@router.get("/{candidate_id}/reveal", response_model=CandidateData)
def reveal_candidate_pii(candidate_id: str):
    """Reveals unmasked candidate identity and records a PII_REVEALED audit event."""
    cand = database.get_candidate(candidate_id)
    if not cand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    record_audit_event(
        event_type="PII_REVEALED",
        candidate_id=candidate_id,
        actor="Recruiter",
        details={"candidate_id": candidate_id, "anonymized_id": cand.anonymized_name}
    )
    return anonymize_candidate(cand, strip=False)

@router.patch("/{candidate_id}/status", response_model=CandidateData)
def update_candidate_status_endpoint(candidate_id: str, req: StatusUpdateRequest):
    """Updates candidate lifecycle status (NEW, UNDER_REVIEW, SHORTLISTED, INTERVIEW, REJECTED, HIRED)."""
    cand = database.update_candidate_status(candidate_id, req.status)
    if not cand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    record_audit_event(
        event_type="STATUS_CHANGED",
        candidate_id=candidate_id,
        actor="Recruiter",
        details={"new_status": req.status}
    )
    return cand

@router.post("/{candidate_id}/notes", response_model=CandidateData)
def add_candidate_note_endpoint(candidate_id: str, req: RecruiterNoteRequest):
    """Appends an interview note or review comment to candidate dossier."""
    if not req.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note text cannot be empty")
    cand = database.add_recruiter_note(candidate_id, req.text, author=req.author or "Recruiter")
    if not cand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    record_audit_event(
        event_type="RECRUITER_NOTE_ADDED",
        candidate_id=candidate_id,
        actor=req.author or "Recruiter",
        details={"note_preview": req.text[:60]}
    )
    return cand

@router.post("/compare", response_model=CandidateComparisonResponse)
def compare_candidates_endpoint(req: CandidateComparisonRequest):
    """Generates side-by-side evaluation comparison across multiple candidates for a role."""
    if not req.candidate_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide at least one candidate ID")
    try:
        comparison = database.compare_candidates_for_job(req.candidate_ids, req.job_id)
        record_audit_event(
            event_type="CANDIDATES_COMPARED",
            job_id=req.job_id,
            actor="Recruiter",
            details={"candidate_count": len(req.candidate_ids)}
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/upload", response_model=List[CandidateData])
async def upload_resumes(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided in upload request.")

    saved_candidates: List[CandidateData] = []

    for f in files:
        raw_filename = f.filename or ""
        ext = os.path.splitext(raw_filename)[1].lower()

        # Extension validation
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type '{ext}' for file '{raw_filename}'. Allowed types: .pdf, .txt"
            )

        # Content-type check
        if f.content_type and f.content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid MIME type '{f.content_type}' for file '{raw_filename}'."
            )

        # Sanitize filename & random disk storage
        safe_name = sanitize_filename(raw_filename)
        file_id = str(uuid.uuid4())
        unique_disk_name = f"{file_id}_{safe_name}"
        dest_path = os.path.join(settings.UPLOADS_DIR, unique_disk_name)

        # Stream & 10MB size limit check
        file_size = 0
        try:
            with open(dest_path, "wb") as buffer:
                while True:
                    chunk = await f.read(1024 * 1024)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > MAX_FILE_SIZE_BYTES:
                        buffer.close()
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File '{raw_filename}' exceeds maximum allowed upload size of 10MB."
                        )
                    buffer.write(chunk)
        except HTTPException:
            raise
        except Exception as e:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File write failed: {str(e)}")

        record_audit_event(
            event_type="RESUME_UPLOAD",
            actor="Recruiter",
            details={"filename": safe_name, "size_bytes": file_size}
        )

        # Extract text with timeout protection
        raw_text = ""
        try:
            if ext == ".pdf":
                loop = asyncio.get_running_loop()
                raw_text, _ = await asyncio.wait_for(
                    loop.run_in_executor(None, extract_raw_text_from_pdf, dest_path),
                    timeout=EXTRACTION_TIMEOUT_SECONDS
                )
            else:
                with open(dest_path, "r", encoding="utf-8", errors="ignore") as tf:
                    raw_text = tf.read()
        except asyncio.TimeoutError:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=f"Document parsing timed out for '{raw_filename}'."
            )
        except Exception as e:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse text from '{raw_filename}': {str(e)}"
            )

        # Parse candidate & enrich
        candidate = parse_resume_to_candidate(raw_text, filename=safe_name)
        candidate = enrich_candidate_with_evidence(candidate)

        if settings.ENABLE_LINK_CHECK and candidate.external_links:
            try:
                candidate.external_links = await verify_candidate_links(candidate.external_links)
            except Exception as e:
                logger.warning(f"Link verification error for candidate {candidate.candidate_id}: {e}")

        database.save_candidate(candidate)

        # Record upload link in DB
        conn = database.get_connection()
        c_cur = conn.cursor()
        c_cur.execute("""
        INSERT INTO uploads (upload_id, filename, file_path, candidate_id, file_size, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (file_id, safe_name, dest_path, candidate.candidate_id, file_size, candidate.created_at or ""))
        conn.commit()
        conn.close()

        record_audit_event(
            event_type="RESUME_PARSED",
            candidate_id=candidate.candidate_id,
            actor="system",
            details={"skills_count": len(candidate.skills), "tenure_years": candidate.total_experience_years}
        )

        saved_candidates.append(candidate)

    return saved_candidates

@router.delete("/{candidate_id}")
def delete_candidate_endpoint(candidate_id: str):
    success = database.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    record_audit_event(
        event_type="CANDIDATE_DELETED",
        candidate_id=candidate_id,
        actor="Recruiter",
        details={"candidate_id": candidate_id}
    )
    return {"status": "success", "message": "Candidate and associated files deleted", "candidate_id": candidate_id}

@router.delete("")
def clear_all_candidates_endpoint():
    count = database.delete_all_candidates()
    record_audit_event(
        event_type="ALL_CANDIDATES_CLEARED",
        actor="Recruiter",
        details={"deleted_count": count}
    )
    return {"status": "success", "message": "Cleared all candidate records and upload files", "deleted_count": count}
