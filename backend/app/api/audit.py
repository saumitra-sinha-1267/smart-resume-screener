from typing import List, Optional
from fastapi import APIRouter, Query
from app.core.audit import get_audit_logs
from app.normalization.schema_models import AuditLogEntry

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogEntry])
def list_audit_logs(
    candidate_id: Optional[str] = Query(None, description="Filter by candidate ID"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, description="Max number of logs to return")
):
    """Returns tamper-evident structured audit trail without revealing raw unmasked candidate PII."""
    return get_audit_logs(candidate_id=candidate_id, job_id=job_id, event_type=event_type, limit=limit)
