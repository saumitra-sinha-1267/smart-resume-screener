import json
import uuid
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core import database
from app.normalization.schema_models import AuditLogEntry

EMAIL_REGEX = r"[a-zA-Z0-9_.+%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}"

def sanitize_audit_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures no raw unmasked email, phone, or sensitive candidate PII is persisted in audit logs."""
    sanitized = {}
    for k, v in details.items():
        if isinstance(v, str):
            clean_str = re.sub(EMAIL_REGEX, "[EMAIL_MASKED]", v)
            clean_str = re.sub(PHONE_REGEX, "[PHONE_MASKED]", clean_str)
            sanitized[k] = clean_str
        elif isinstance(v, dict):
            sanitized[k] = sanitize_audit_details(v)
        elif isinstance(v, list):
            sanitized[k] = [sanitize_audit_details(i) if isinstance(i, dict) else i for i in v]
        else:
            sanitized[k] = v
    return sanitized

def record_audit_event(
    event_type: str,
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    actor: str = "system",
    details: Optional[Dict[str, Any]] = None
) -> AuditLogEntry:
    """Records a secure audit log event."""
    log_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    clean_details = sanitize_audit_details(details or {})

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (
        log_id, event_type, candidate_id, job_id, actor, details_json, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        log_id,
        event_type,
        candidate_id,
        job_id,
        actor,
        json.dumps(clean_details, ensure_ascii=False),
        now
    ))
    conn.commit()
    conn.close()

    return AuditLogEntry(
        log_id=log_id,
        event_type=event_type,
        candidate_id=candidate_id,
        job_id=job_id,
        actor=actor,
        details=clean_details,
        timestamp=now
    )

def get_audit_logs(
    candidate_id: Optional[str] = None,
    job_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50
) -> List[AuditLogEntry]:
    """Fetches audit logs with optional filters."""
    conn = database.get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM audit_logs WHERE 1=1"
    params: List[Any] = []

    if candidate_id:
        query += " AND candidate_id = ?"
        params.append(candidate_id)
    if job_id:
        query += " AND job_id = ?"
        params.append(job_id)
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    entries = []
    for r in rows:
        entries.append(AuditLogEntry(
            log_id=r["log_id"],
            event_type=r["event_type"],
            candidate_id=r["candidate_id"],
            job_id=r["job_id"],
            actor=r["actor"],
            details=json.loads(r["details_json"]),
            timestamp=r["timestamp"]
        ))
    return entries
