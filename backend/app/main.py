import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core import database
from app.api import candidates, jobs, screening, export, audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    existing_jobs = database.list_jobs()
    if not existing_jobs:
        from app.sample_data.sample_generator import SAMPLE_JOBS, generate_sample_candidates
        for j in SAMPLE_JOBS:
            database.save_job(j)
        for c in generate_sample_candidates():
            database.save_candidate(c)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-powered Smart Resume Screener with PII stripping, dense semantic matching, metric evidence verification, LLM multi-dimension scoring, and hallucination guard.",
    lifespan=lifespan
)

@app.on_event("startup")
def startup_event():
    database.init_db()
    existing_jobs = database.list_jobs()
    if not existing_jobs:
        from app.sample_data.sample_generator import SAMPLE_JOBS, generate_sample_candidates
        for j in SAMPLE_JOBS:
            database.save_job(j)
        for c in generate_sample_candidates():
            database.save_candidate(c)

cors_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix=settings.API_PREFIX)
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(screening.router, prefix=settings.API_PREFIX)
app.include_router(export.router, prefix=settings.API_PREFIX)
app.include_router(audit.router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    candidates_count = len(database.list_candidates())
    jobs_count = len(database.list_jobs())
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "SQLite (Connected)",
        "stats": {
            "total_candidates": candidates_count,
            "total_jobs": jobs_count
        },
        "features": {
            "pii_stripping": True,
            "evidence_verification": True,
            "semantic_vector_prefilter": True,
            "dense_embeddings": "sentence-transformers/all-MiniLM-L6-v2",
            "ocr_fallback": True,
            "llm_scoring": True,
            "hallucination_guard": True,
            "confidence_scorer": True,
            "trajectory_analysis": True
        }
    }
