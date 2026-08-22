# Smart Resume Screener (Enterprise ATS & AI Screening Engine)

A high-throughput, enterprise-grade AI resume screening and applicant tracking platform designed for talent acquisition teams. It combines **local semantic vector retrieval (`sentence-transformers/all-MiniLM-L6-v2`)**, **structured LLM evaluation**, **deterministic calibrated fallback scoring**, **claim-by-claim hallucination guarding**, and **blind review privacy enforcement**.

---

## 1. System Architecture

```
                                  +---------------------------------------+
                                  | React + Vite + TypeScript (ATS UI)    |
                                  | - Candidate Table with Filters        |
                                  | - Blind Review Redaction Toggle       |
                                  | - Side-by-Side Candidate Comparison   |
                                  | - Compliance Audit Log Trail          |
                                  +-------------------+-------------------+
                                                      | HTTP / REST
                                                      v
                                  +---------------------------------------+
                                  | FastAPI Backend Application           |
                                  | - Upload Validation (10MB, PDF/TXT)   |
                                  | - PII Stripping & Anonymization Engine|
                                  | - SSRF-Protected External Link Checker|
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +----------------------+
                     v                                                                 v
+------------------------------------------+                      +------------------------------------------+
| Semantic Retrieval Pipeline              |                      | Multi-Dimension Evaluation Pipeline      |
| 1. Chunk Resume Bullets                  |                      | 1. Hard Requirements (Mandatory Skills)  |
| 2. Dense Embeddings (all-MiniLM-L6-v2)   |                      | 2. Soft Requirements (Preferred/Domain)  |
| 3. Global In-Memory Vector Cache         |                      | 3. LLM Evaluator (Gemini / OpenAI)       |
| 4. Cosine Similarity Pre-filtering (Top N|                      | 4. Deterministic Calibrated Fallback     |
+------------------------------------------+                      | 5. Hallucination Guard (Claim Audit)     |
                                                                  | 6. Multi-Factor Confidence Index         |
                                                                  +--------------------+---------------------+
                                                                                       |
                                                                                       v
                                                                  +------------------------------------------+
                                                                  | SQLite Storage Engine (WAL Mode)         |
                                                                  | - Compound Indexes on Screenings/Uploads |
                                                                  | - Tamper-Evident PII-Sanitized Audit Logs|
                                                                  +------------------------------------------+
```

---

## 2. Core Features

### Enterprise Recruiter Dashboard
- **Real-Time KPIs**: Total Candidates, Screened, Shortlisted, Interviews.
- **Table-Heavy Interface**: Search, Job filter, Status filter, Score filter, Multi-select bulk shortlisting, and candidate comparison.
- **Compact Progress Bars**: Visualizes overall score (`92% [█████████░]`) and sub-dimensions without circular gauges.

### Job Description Intelligence
- **AI JD Analyzer**: Pasting raw job description automatically extracts Title, Department, Seniority, Min Experience, Mandatory Skills, and Preferred Skills.
- **Editable Requirements**: Recruiters can modify extracted chips and criteria before saving.

### 5-Dimension Scoring Matrix
1. **Skills Alignment (30%)**: Matches extracted skills against job taxonomy.
2. **Experience Depth (25%)**: Compares verified tenure against minimum years.
3. **Evidence Quality (20%)**: Categorizes bullet points into **STRONG** (quantified outcome metrics: latency, scale, headcount, revenue), **MEDIUM** (technical actions), and **WEAK** (generic duties).
4. **Seniority Alignment (15%)**: Assesses title progression and career trajectory.
5. **Education Fit (10%)**: Degree level and academic specialization fit.

### Security, Safety & Privacy
- **Blind Review PII Redaction**: Hides candidate names, emails, phone numbers, and graduation years to mitigate unconscious bias.
- **SSRF Attack Shield**: Resolves domain IPs and blocks private networks (RFC 1918), AWS/GCP metadata services (`169.254.169.254`), and loopback addresses.
- **Upload Security**: 10MB file limit, MIME allowlisting (`.pdf`, `.txt`), path traversal defense, and PDF parsing timeout protection.
- **Prompt Injection Defense**: Sanitizes input bullets against instruction injection and prompt override payloads.
- **Audit Logging**: Immutable SQLite audit log tracking all actions with automated email/phone scrubbing.

---

## 3. Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Google Gemini API Key or OpenAI API Key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API documentation will be accessible at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install npm packages
npm install

# Run Vite development server
npm run dev
```

Frontend UI will be accessible at: `http://localhost:5173`

---

## 4. Environment Variables Reference

| Variable | Default | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `""` | Optional Google Gemini API key for LLM candidate evaluation. |
| `OPENAI_API_KEY` | `""` | Optional OpenAI API key alternative. |
| `GITHUB_TOKEN` | `""` | Optional GitHub Personal Access Token to increase link verification rate limits (60/hr $ightarrow$ 5000/hr). |
| `TOP_N_FILTER` | `15` | Number of top candidates retrieved via vector pre-filtering before deep evaluation. |
| `ENABLE_LINK_CHECK` | `true` | Toggles external link liveness and security verification. |
| `DATABASE_PATH` | `data/screener.db` | Custom path for SQLite database. |
| `UPLOADS_DIR` | `data/uploads` | Directory for uploaded resume documents. |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins for CORS headers. |

---

## 5. AI Evaluation & Benchmark Framework

Smart Resume Screener includes an offline evaluation framework with labelled synthetic benchmark datasets:

```bash
cd backend
python -m evaluation.run
```

### Calculated Benchmark Results:

```
================================================================================
SMART RESUME SCREENER — AI EVALUATION SUITE
================================================================================

[1] DATASET OVERVIEW:
  • Total Candidates: 10
  • Ground Truth Relevant (>=2): 4
  • Target Benchmark Role: Senior Backend Engineer

[2] RANKING QUALITY METRICS:
  • Precision@5: 0.8000 (Target: > 0.80)
  • Recall@10:   1.0000 (Target: 1.00)
  • NDCG@10:     0.9988 (Target: > 0.85)
  • MRR:         1.0000 (Target: 1.00)

[3] ERROR & CLASSIFICATION METRICS:
  • False Positive Rate: 0.0000
  • False Negative Rate: 0.2500

[4] BIAS & CONSISTENCY AUDIT:
  • Tested Variables: Name, Location, Graduation Year, Email Domain
  • Mean Absolute Difference: 0.0000
  • Max Delta Observed:       0.0000
  • Status: PASS (Robust Consistency)

[5] CONFIDENCE CALIBRATION:
  • Unjustified High Rate: 0.0000
================================================================================
```

---

## 6. Running Tests

### Backend Test Suite (41 Tests)
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Test Suite & Production Build
```bash
cd frontend
npx vitest run
npm run build
```

---

## 7. Known Limitations & Production Roadmap

1. **OCR Processing**: Scanned image PDFs rely on system `tesseract-ocr` binary if available; when unavailable, it falls back to graceful text extraction.
2. **Database Engine**: Uses SQLite in Write-Ahead Logging (WAL) mode for low-latency concurrent operations. For multi-tenant distributed deployments, migrate `database.py` connection to PostgreSQL.
3. **Async Celery Queue**: For processing 10,000+ resumes concurrently in background batches, an asynchronous worker queue (Celery/Redis or Temporal) is recommended.
