import re
from typing import List, Tuple, Dict, Any
from app.normalization.schema_models import CandidateData, JobData, JobRequirement, RequirementMatch
from app.normalization.taxonomy import SKILL_SYNONYMS
from app.evidence.metric_detector import classify_evidence_quality

def match_candidate_to_requirements(candidate: CandidateData, job: JobData) -> List[RequirementMatch]:
    """Evaluates each individual job requirement and returns MATCHED | PARTIAL | INFERRED | MISSING with supporting quotes."""
    matches: List[RequirementMatch] = []
    
    # Auto-synthesize requirements if job.requirements is empty
    req_list = list(job.requirements)
    if not req_list:
        if job.min_experience_years > 0:
            req_list.append(JobRequirement(
                text=f"{job.min_experience_years}+ years relevant experience",
                category="experience",
                weight=1.5,
                required=True,
                is_mandatory=True
            ))
        for s in job.required_skills:
            req_list.append(JobRequirement(
                text=f"Hands-on expertise in {s}",
                category="skill",
                weight=1.0,
                required=True,
                is_mandatory=True
            ))
        for p in job.preferred_skills:
            req_list.append(JobRequirement(
                text=f"Familiarity with {p}",
                category="skill",
                weight=0.5,
                required=False,
                is_mandatory=False
            ))
    cand_skill_map = {s.name.lower(): s for s in candidate.skills}
    cand_text_lower = (candidate.raw_text or "").lower()

    # Collect all candidate bullets with their strength
    bullet_records: List[Tuple[str, str]] = [] # (bullet_text, strength)
    for exp in candidate.experience:
        for b in exp.bullets:
            st, _ = classify_evidence_quality(b)
            bullet_records.append((b, st))

    for req in req_list:
        req_lower = req.text.lower()
        req_cat = req.category.lower()
        is_mand = req.is_mandatory or req.required

        status = "MISSING"
        strength = "NONE"
        evidence_quotes: List[str] = []
        reasoning = ""

        # 1. Experience Requirements
        if req_cat == "experience" or "year" in req_lower:
            # Extract requested years
            exp_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*year", req_lower)
            req_years = float(exp_match.group(1)) if exp_match else job.min_experience_years
            actual_years = candidate.total_experience_years

            if req_years == 0.0 or job.min_experience_years == 0.0:
                status = "MATCHED"
                strength = "STRONG"
                reasoning = f"Candidate profile ({actual_years} yrs verified) satisfies entry-level / 0+ years requirement."
                if candidate.experience:
                    evidence_quotes.append(f"{candidate.experience[0].title} ({actual_years} yrs)")
            elif actual_years >= req_years:
                status = "MATCHED"
                strength = "STRONG" if actual_years >= req_years + 2 else "MEDIUM"
                reasoning = f"Verified {actual_years} years of relevant experience, satisfying the {req_years} years minimum."
                if candidate.experience:
                    evidence_quotes.append(f"{candidate.experience[0].title} ({actual_years} total years)")
            elif actual_years >= req_years * 0.6:
                status = "PARTIAL"
                strength = "MEDIUM"
                reasoning = f"Candidate possesses {actual_years} years experience, partially fulfilling the requested {req_years} years."
            else:
                status = "MISSING"
                strength = "WEAK"
                reasoning = f"Tenure gap: {actual_years} years vs {req_years} years required."

        # 2. Skill Requirements
        elif req_cat == "skill":
            target_skill = ""
            for s_name in job.required_skills + job.preferred_skills:
                if s_name.lower() in req_lower:
                    target_skill = s_name
                    break

            if not target_skill:
                # Find any canonical skill mention in requirement text
                for alias, canonical in SKILL_SYNONYMS.items():
                    if alias in req_lower:
                        target_skill = canonical
                        break

            found_item = cand_skill_map.get(target_skill.lower()) if target_skill else None
            
            # Special skill synonym/sub-skill mapping for Data Visualization & Analytics
            sub_skills = []
            if target_skill.lower() in ["data visualization", "data visualisation", "visualization"]:
                sub_skills = ["plotly", "power bi", "tableau", "matplotlib", "seaborn", "streamlit"]
            elif target_skill.lower() in ["statistics", "statistical analysis"]:
                sub_skills = ["hypothesis testing", "regression", "a/b testing", "statistical modeling", "anova"]
            elif target_skill.lower() in ["sql"]:
                sub_skills = ["mysql", "postgresql", "sqlite", "sql server"]

            matched_sub_items = [cand_skill_map[s] for s in sub_skills if s in cand_skill_map]

            # Also check text mentions
            matched_bullets = []
            if target_skill:
                for b, b_str in bullet_records:
                    if target_skill.lower() in b.lower() or any(s in b.lower() for s in sub_skills):
                        matched_bullets.append((b, b_str))

            if (found_item and found_item.source != "inferred_from_bullet") or (target_skill and target_skill.lower() in cand_text_lower):
                status = "MATCHED"
                if matched_bullets:
                    best_strength = "STRONG" if any(m[1] == "STRONG" for m in matched_bullets) else "MEDIUM"
                    strength = best_strength
                    evidence_quotes.extend([m[0] for m in matched_bullets[:2]])
                    reasoning = f"Explicitly verified expertise in '{target_skill}' backed by {len(matched_bullets)} work/project bullet(s)."
                else:
                    strength = "MEDIUM"
                    reasoning = f"Skill '{target_skill}' listed in technical credentials."
            elif matched_sub_items:
                # E.g. Candidate has Plotly/Streamlit for Data Visualization
                status = "MATCHED" if len(matched_sub_items) >= 2 else "PARTIAL"
                strength = "MEDIUM"
                sub_names = ", ".join([s.name for s in matched_sub_items])
                reasoning = f"Evidenced via supporting tooling: {sub_names}."
                if matched_bullets:
                    evidence_quotes.extend([m[0] for m in matched_bullets[:2]])
            elif found_item and found_item.source == "inferred_from_bullet":
                status = "PARTIAL"
                strength = found_item.evidence_strength if found_item.evidence_strength != "NONE" else "WEAK"
                reasoning = f"Indirectly supported: inferred '{target_skill}' from candidate project/experience statements."
                if matched_bullets:
                    evidence_quotes.extend([m[0] for m in matched_bullets[:2]])
            else:
                status = "MISSING"
                strength = "NONE"
                reasoning = f"Required skill '{target_skill or req.text}' not evidenced in resume."

        # 3. Education Requirements
        elif req_cat == "education":
            if candidate.education:
                edu_text = candidate.education[0].degree
                from app.normalization.taxonomy import classify_degree_alignment
                status, strength, reasoning = classify_degree_alignment(edu_text)
                evidence_quotes.append(edu_text)
            else:
                status = "MISSING"
                strength = "NONE"
                reasoning = "Degree credential masked or unlisted."

        # 4. Domain & Leadership Requirements
        elif req_cat in ["domain", "leadership"]:
            matching_b = [b for b, _ in bullet_records if any(w in b.lower() for w in req_lower.split() if len(w) > 4)]
            if matching_b:
                status = "MATCHED"
                strength = "MEDIUM"
                evidence_quotes.extend(matching_b[:2])
                reasoning = f"Demonstrated {req_cat} experience in project history."
            else:
                status = "MISSING"
                strength = "NONE"
                reasoning = f"No direct evidence found for {req.text}."

        # 5. Generic / Responsibility Requirements
        else:
            matching_b = [b for b, _ in bullet_records if any(w in b.lower() for w in req_lower.split() if len(w) > 4)]
            if matching_b:
                status = "MATCHED"
                strength = "MEDIUM"
                evidence_quotes.extend(matching_b[:2])
                reasoning = f"Demonstrated background matching: {req.text}"
            else:
                status = "PARTIAL"
                strength = "WEAK"
                reasoning = f"Broad alignment inferred from career experience."

        matches.append(RequirementMatch(
            requirement_id=req.id,
            text=req.text,
            category=req_cat,
            is_mandatory=is_mand,
            status=status,
            supporting_evidence=evidence_quotes,
            evidence_strength=strength,
            reasoning=reasoning
        ))

    return matches
