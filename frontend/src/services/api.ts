import {
  CandidateData,
  JobData,
  ScreeningResult,
  CandidateStatus,
  AuditLogEntry,
  CandidateComparisonResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export async function fetchJobs(): Promise<JobData[]> {
  const res = await fetch(`${API_BASE}/jobs`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch jobs (HTTP ${res.status})`);
  }
  return res.json();
}

export async function getJob(jobId: string): Promise<JobData> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch job (HTTP ${res.status})`);
  }
  return res.json();
}

export async function createJob(job: Partial<JobData>): Promise<JobData> {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(job),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create job (HTTP ${res.status})`);
  }
  return res.json();
}

export async function parseJobDescription(rawDescription: string, title?: string): Promise<JobData> {
  const res = await fetch(`${API_BASE}/jobs/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_description: rawDescription, title }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to analyze job description (HTTP ${res.status})`);
  }
  return res.json();
}

export async function fetchCandidates(anonymized = true): Promise<CandidateData[]> {
  const res = await fetch(`${API_BASE}/candidates?anonymized=${anonymized}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch candidates (HTTP ${res.status})`);
  }
  return res.json();
}

export async function getCandidate(candidateId: string, anonymized = true): Promise<CandidateData> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}?anonymized=${anonymized}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to load candidate (HTTP ${res.status})`);
  }
  return res.json();
}

export async function revealCandidatePii(candidateId: string): Promise<CandidateData> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}/reveal`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to reveal candidate PII (HTTP ${res.status})`);
  }
  return res.json();
}

export async function updateCandidateStatus(candidateId: string, status: CandidateStatus): Promise<CandidateData> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update status (HTTP ${res.status})`);
  }
  return res.json();
}

export async function addCandidateNote(candidateId: string, text: string, author = 'Recruiter'): Promise<CandidateData> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, author }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to record note (HTTP ${res.status})`);
  }
  return res.json();
}

export async function deleteCandidate(candidateId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}`, { method: 'DELETE' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to delete candidate (HTTP ${res.status})`);
  }
}

export async function clearAllCandidates(): Promise<void> {
  const res = await fetch(`${API_BASE}/candidates`, { method: 'DELETE' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to clear candidates (HTTP ${res.status})`);
  }
}

export async function uploadResumes(files: File[]): Promise<CandidateData[]> {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));

  const res = await fetch(`${API_BASE}/candidates/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to upload resumes (HTTP ${res.status})`);
  }
  return res.json();
}

export async function runScreening(jobId: string, topN = 15, anonymized = true): Promise<ScreeningResult[]> {
  const res = await fetch(`${API_BASE}/screen/${jobId}?top_n=${topN}&anonymized=${anonymized}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Screening pipeline failed (HTTP ${res.status})`);
  }
  return res.json();
}

export async function fetchExistingResults(jobId: string, anonymized = true): Promise<ScreeningResult[]> {
  const res = await fetch(`${API_BASE}/screen/${jobId}/results?anonymized=${anonymized}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to load screening results (HTTP ${res.status})`);
  }
  return res.json();
}

export async function compareCandidates(candidateIds: string[], jobId: string): Promise<CandidateComparisonResponse> {
  const res = await fetch(`${API_BASE}/candidates/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ candidate_ids: candidateIds, job_id: jobId }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Comparison failed (HTTP ${res.status})`);
  }
  return res.json();
}

export async function fetchAuditLogs(params?: {
  candidate_id?: string;
  job_id?: string;
  event_type?: string;
  limit?: number;
}): Promise<AuditLogEntry[]> {
  const query = new URLSearchParams();
  if (params?.candidate_id) query.set('candidate_id', params.candidate_id);
  if (params?.job_id) query.set('job_id', params.job_id);
  if (params?.event_type) query.set('event_type', params.event_type);
  if (params?.limit) query.set('limit', String(params.limit));

  const res = await fetch(`${API_BASE}/audit-logs?${query.toString()}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch audit logs (HTTP ${res.status})`);
  }
  return res.json();
}

export async function seedDemoData(): Promise<void> {
  const res = await fetch(`${API_BASE}/sample-data/seed`, { method: 'POST' });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to seed demo data (HTTP ${res.status})`);
  }
}

export function getExportUrl(jobId: string): string {
  return `${API_BASE}/export/${jobId}/csv`;
}
