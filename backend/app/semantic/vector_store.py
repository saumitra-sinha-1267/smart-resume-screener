import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from app.normalization.schema_models import CandidateData, JobData
from app.semantic.embedding_engine import SentenceEmbedder

# Global vector cache across instances: {candidate_id: (bullets_hash, ndarray)}
_GLOBAL_VECTOR_CACHE: Dict[str, Tuple[int, np.ndarray]] = {}

class CandidateVectorIndex:
    """Indexes candidates at the bullet level with dense embeddings, embedding caching, and fast Top-N pre-filtering."""

    def __init__(self):
        self.embedder = SentenceEmbedder()
        self.candidate_bullets: Dict[str, List[str]] = {}
        self.candidate_vectors: Dict[str, np.ndarray] = {}

    def index_candidates(self, candidates: List[CandidateData]):
        for c in candidates:
            bullets = []
            for exp in c.experience:
                bullets.extend(exp.bullets)
            if c.skills:
                bullets.append("Proficient in " + ", ".join(s.name for s in c.skills))
            self.candidate_bullets[c.candidate_id] = bullets

            if not bullets:
                self.candidate_vectors[c.candidate_id] = np.empty((0, 384), dtype=np.float32)
                continue

            # Check global vector cache
            bullets_hash = hash(tuple(bullets))
            cached = _GLOBAL_VECTOR_CACHE.get(c.candidate_id)
            if cached and cached[0] == bullets_hash:
                self.candidate_vectors[c.candidate_id] = cached[1]
            else:
                encoded = self.embedder.encode(bullets)
                _GLOBAL_VECTOR_CACHE[c.candidate_id] = (bullets_hash, encoded)
                self.candidate_vectors[c.candidate_id] = encoded

    def match_bullet_to_requirements(self, bullet_vec: np.ndarray, req_matrix: np.ndarray) -> float:
        """Finds max cosine similarity between a resume bullet vector and all requirement vectors."""
        if req_matrix is None or len(req_matrix) == 0 or bullet_vec is None or len(bullet_vec) == 0:
            return 0.0
        dots = np.dot(req_matrix, bullet_vec)
        return float(np.max(dots)) if len(dots) > 0 else 0.0

    def prefilter_top_candidates(self, job: JobData, candidates: List[CandidateData], top_n: int = 15) -> List[Tuple[CandidateData, float]]:
        """Ranks candidates by dense semantic similarity against job requirements and returns top-N."""
        if not candidates:
            return []

        self.index_candidates(candidates)

        req_texts = [r.text for r in job.requirements] if job.requirements else [job.raw_description]
        if job.required_skills:
            req_texts.append("Required skills: " + ", ".join(job.required_skills))
        req_matrix = self.embedder.encode(req_texts)

        scored_candidates: List[Tuple[CandidateData, float]] = []
        for cand in candidates:
            c_matrix = self.candidate_vectors.get(cand.candidate_id)
            if c_matrix is None or len(c_matrix) == 0:
                scored_candidates.append((cand, 0.0))
                continue

            dots = np.dot(c_matrix, req_matrix.T) # shape: (num_bullets, num_reqs)
            max_per_bullet = np.max(dots, axis=1)
            similarities = sorted(list(max_per_bullet), reverse=True)

            top_k = similarities[:3]
            top_k_avg = float(sum(top_k) / len(top_k)) if top_k else 0.0
            overall_avg = float(sum(similarities) / len(similarities)) if similarities else 0.0

            cand_skill_names = {s.name.lower() for s in cand.skills}
            req_skill_names = {s.lower() for s in job.required_skills}
            overlap = len(cand_skill_names & req_skill_names)
            skill_bonus = (overlap / len(req_skill_names)) * 0.3 if req_skill_names else 0.0

            total_prefilter_score = (top_k_avg * 0.5) + (overall_avg * 0.2) + skill_bonus
            scored_candidates.append((cand, round(float(total_prefilter_score), 4)))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:top_n]
