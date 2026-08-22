import re
from typing import Dict, Any, List
from app.normalization.schema_models import CandidateData

SENIORITY_RANKS = {
    "intern": 1,
    "trainee": 1,
    "associate": 2,
    "junior": 2,
    "software engineer": 3,
    "developer": 3,
    "data scientist": 3,
    "backend engineer": 3,
    "frontend engineer": 3,
    "full stack engineer": 3,
    "senior": 4,
    "staff": 5,
    "principal": 5,
    "lead": 5,
    "architect": 5,
    "engineering manager": 5,
    "manager": 5,
    "director": 6,
    "head of": 6,
    "vp": 6,
    "chief": 7,
    "cto": 7
}

def get_title_rank(title: str) -> int:
    title_lower = title.lower()
    for keyword, rank in sorted(SENIORITY_RANKS.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in title_lower:
            return rank
    return 3 # Default mid-level

def analyze_career_trajectory(candidate: CandidateData) -> Dict[str, Any]:
    """Analyzes chronological role progression, title advancement, and stack expansion."""
    if not candidate.experience:
        return {
            "progression_type": "Insufficient Data",
            "title_growth": "No experience entries found",
            "stack_expansion_count": 0,
            "job_hopping_flag": False,
            "average_tenure_years": 0.0,
            "is_heuristic": True,
            "disclaimer": "Supporting heuristic signal; non-predictive of individual capability."
        }
        
    ranks = [get_title_rank(e.title) for e in candidate.experience]
    # Check if chronological progression is ascending (older roles first, or reverse)
    # Experience is usually top (most recent) to bottom (oldest)
    reversed_ranks = list(reversed(ranks))
    
    is_advancing = False
    if len(reversed_ranks) >= 2:
        if reversed_ranks[-1] >= reversed_ranks[0]:
            is_advancing = True
            
    # Track unique skills added over time
    all_seen_skills = set()
    skills_added_per_role = []
    for exp in reversed(candidate.experience):
        new_skills = set(exp.extracted_skills) - all_seen_skills
        skills_added_per_role.append({
            "role": exp.title,
            "new_skills_added": sorted(list(new_skills))
        })
        all_seen_skills.update(exp.extracted_skills)
        
    # Check tenure and job-hopping pattern (e.g. >= 3 roles under 8 months)
    short_stints = 0
    for exp in candidate.experience:
        if exp.duration_months and exp.duration_months < 8:
            short_stints += 1
            
    job_hopping = (short_stints >= 3 and len(candidate.experience) >= 3)
    avg_tenure = round(candidate.total_experience_years / max(1, len(candidate.experience)), 1)
    
    progression_type = "Steady Growth" if is_advancing else "Lateral Mastery"
    if len(ranks) == 1:
        progression_type = "Single Track"
        
    return {
        "progression_type": progression_type,
        "title_growth": f"Moved from rank {reversed_ranks[0]} to rank {reversed_ranks[-1]}" if len(reversed_ranks) >= 2 else "Established Role",
        "stack_expansion_count": len(all_seen_skills),
        "role_timeline": skills_added_per_role,
        "job_hopping_flag": job_hopping,
        "average_tenure_years": avg_tenure,
        "is_heuristic": True,
        "disclaimer": "Supporting heuristic signal; non-predictive of individual capability."
    }
