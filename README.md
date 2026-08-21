# Smart Resume Screener — AI-Powered Autonomous Candidate Evaluation

A production-grade, end-to-end Smart Resume Screener system built following a strict 11-step pipeline with extraction, normalization, semantic pre-filtering, metric evidence detection, LLM multi-dimension scoring, hallucination guard, confidence index, and interactive UI.

---

## High-Level Architecture & Workflow

```
[Resumes PDF/TXT] + [Job Description]
       │
       ▼
1. EXTRACTION LAYER (pypdf + layout-aware chunking + OCR fallback)
       │
       ▼
2. NORMALIZATION LAYER (500+ Skill taxonomy mapping + Strict PII Stripping)
       │
       ▼
3. STORAGE LAYER (SQLite persistent candidates, jobs, scores, audit log)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
4. SEMANTIC MATCH LAYER           5. EVIDENCE VERIFICATION LAYER
   • Vector TF-IDF / Embeddings      • Regex/NER quantified outcome detector (%, ms, $, scale)
   • Cosine similarity pre-filter    • Async HTTP & GitHub API liveness verification
       │                                 │
       └────────────────┬────────────────┘
                        ▼
6. LLM MULTI-DIMENSION SCORING LAYER (Gemini API / Calibrated offline engine)
   • Skills Match (0-10)
   • Experience Relevance (0-10)
   • Seniority Alignment (0-10)
   • Education Fit (0-10)
       │
       ▼
7. HALLUCINATION GUARD (Cross-checks LLM matched claims against extracted ground truth)
       │
       ▼
8. MULTI-FACTOR CONFIDENCE SCORING (Completeness + Evidence density + Link status)
       │
       ▼
9. CAREER TRAJECTORY HEURISTIC (Chronological role progression & stack expansion)
       │
       ▼
10. FASTAPI REST API + REACT 18 / TAILWIND DASHBOARD
```

---

## Key Features

1. **Strict PII Anonymization**: Real-time masking of candidate names, graduation years, locations, phone numbers, and emails with a global toggle switch.
2. **Quantified Evidence Verification**: Detects and highlights concrete metric achievements (e.g. `reduced latency by 42%`, `20M daily requests`, `$180k savings`) vs generic unquantified claims.
3. **External Link & GitHub Liveness Check**: Validates candidate GitHub profiles and repositories via live HTTP/API pings, reporting public repos, stars, and last active dates.
4. **Hallucination Guard**: Automatically audits every claim the LLM cites as matched. Unverifiable claims are flagged and discounted with a logged audit trail.
5. **Multi-Factor Confidence Indicator**: Assigns `High`, `Medium`, or `Low` confidence ratings based on resume completeness, metric density, and link verification.
6. **Career Trajectory Heuristic**: Analyzes title advancement and tech-stack growth across time with an explicit non-predictive heuristic disclaimer.
7. **Instant Live Demo**: Preloaded benchmark candidates and multiple tech job descriptions (Senior Backend Engineer, Full Stack AI Engineer, DevOps Lead) with one-click screening.

---

## Quickstart Guide

### 1. Backend Setup & Startup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup & Startup
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be live at `http://localhost:5173`.

### 3. Run Automated Tests
```bash
cd backend
python -m pytest tests/ -v
```
