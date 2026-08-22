import uuid
from typing import List, Dict, Any
from app.normalization.schema_models import JobData, JobRequirement, CandidateData, SkillItem, ExperienceItem, EducationItem, ExternalLinkItem, ContactInfo
from app.normalization.pii_stripper import generate_anonymized_id, mask_email, mask_phone
from app.evidence.metric_detector import enrich_candidate_with_evidence

SAMPLE_JOBS = [
    JobData(
        job_id="job-senior-backend-001",
        title="Senior Backend Engineer",
        department="Platform Engineering",
        min_experience_years=5.0,
        required_skills=["Python", "PostgreSQL", "Distributed Systems", "Kubernetes", "REST APIs"],
        preferred_skills=["Redis", "FastAPI", "Docker", "Team Leadership", "Performance Optimization"],
        requirements=[
            JobRequirement(text="5+ years of production experience building high-throughput backend services in Python", category="experience", weight=1.2),
            JobRequirement(text="Deep mastery of relational databases (PostgreSQL), index optimization, and connection pooling", category="skill", weight=1.0),
            JobRequirement(text="Hands-on experience deploying containerized microservices to Kubernetes clusters", category="skill", weight=1.0),
            JobRequirement(text="Demonstrated ability leading squads and mentoring junior software engineers", category="seniority", weight=0.8),
            JobRequirement(text="Bachelor or Master degree in Computer Science or related engineering discipline", category="education", weight=0.6)
        ],
        raw_description="""We are looking for a Senior Backend Engineer to lead the architecture of our core transaction processing engine.
Responsibilities:
- Design, build, and scale low-latency REST APIs handling 50M+ requests per day using Python and FastAPI.
- Optimize complex PostgreSQL queries and database schemas for high write throughput.
- Collaborate cross-functionally with Product, QA, and DevOps to deliver rock-solid distributed systems.
- Mentor engineers, lead code reviews, and establish engineering standards.
Requirements:
- 5+ years building distributed backend systems in Python.
- Proven experience with PostgreSQL, Redis caching, and Docker/Kubernetes in AWS.
- Strong track record of measurable performance tuning and team leadership."""
    ),
    JobData(
        job_id="job-fullstack-ai-002",
        title="Full Stack AI Engineer",
        department="AI Products",
        min_experience_years=3.0,
        required_skills=["React", "TypeScript", "Python", "LLMs / Generative AI", "FastAPI"],
        preferred_skills=["Tailwind CSS", "Next.js", "ChromaDB", "Vector Databases", "LangChain"],
        requirements=[
            JobRequirement(text="3+ years of modern web development using React, TypeScript, and modern state management", category="skill", weight=1.0),
            JobRequirement(text="Strong backend proficiency in Python and FastAPI", category="skill", weight=1.0),
            JobRequirement(text="Experience building RAG pipelines, prompt engineering, and vector database embeddings", category="skill", weight=1.2),
            JobRequirement(text="Fast-paced iterative product mindset with clean UI/UX intuition", category="experience", weight=0.8)
        ],
        raw_description="""Join our AI Product squad to build next-generation intelligent workflows.
You will bridge frontend design and cutting-edge LLM architectures.
Requirements:
- 3+ years experience with React, TypeScript, and Python.
- Practical experience with LLM APIs, embeddings, vector databases (ChromaDB/Pinecone), and RAG.
- Portfolio of live web applications or open source repositories."""
    ),
    JobData(
        job_id="job-devops-lead-003",
        title="DevOps & Cloud Infrastructure Lead",
        department="Infrastructure",
        min_experience_years=6.0,
        required_skills=["AWS", "Kubernetes", "Terraform", "CI/CD", "Docker", "Linux"],
        preferred_skills=["Prometheus", "Grafana", "Python", "Bash / Shell", "Team Leadership"],
        requirements=[
            JobRequirement(text="6+ years managing large-scale multi-region AWS cloud infrastructure", category="experience", weight=1.2),
            JobRequirement(text="Expertise in Infrastructure as Code using Terraform and Helm", category="skill", weight=1.0),
            JobRequirement(text="Production Kubernetes cluster administration, autoscaling, and monitoring", category="skill", weight=1.1),
            JobRequirement(text="Experience driving 99.99% service availability SLAs and incident management", category="experience", weight=0.9)
        ],
        raw_description="""Seeking an Infrastructure Lead to govern our multi-cloud foundation and CI/CD automation pipelines.
Must have deep Terraform, AWS, and Kubernetes experience with proven track record of reducing infrastructure costs and improving build speed."""
    )
]

def generate_sample_candidates() -> List[CandidateData]:
    cands = [
        # Candidate 1: Perfect match for Senior Backend Engineer
        CandidateData(
            candidate_id="cand-alex-001",
            raw_name="Alex Mercer",
            anonymized_name=generate_anonymized_id("Alex Mercer", "cand-alex-001"),
            contact=ContactInfo(
                email="alex.mercer@devtech.io",
                phone="+1 (555) 234-5678",
                location="San Francisco, CA",
                masked_email="al***@devtech.io",
                masked_phone="***-***-5678",
                masked_location="[LOCATION_MASKED]"
            ),
            pii_stripped=True,
            total_experience_years=6.5,
            skills=[
                SkillItem(name="Python", source="explicit_list", quantified_evidence=False),
                SkillItem(name="PostgreSQL", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Kubernetes", source="explicit_list", quantified_evidence=True),
                SkillItem(name="FastAPI", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Redis", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Docker", source="explicit_list", quantified_evidence=False),
                SkillItem(name="REST APIs", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Team Leadership", source="inferred_from_bullet", original_text="Led a cross-functional squad of 6 engineers to rebuild backend", quantified_evidence=True),
                SkillItem(name="Performance Optimization", source="inferred_from_bullet", original_text="Reduced API p99 latency by 42% across 20M daily requests", quantified_evidence=True)
            ],
            experience=[
                ExperienceItem(
                    title="Staff Backend Engineer",
                    company="Stripe / FinScale",
                    start_date="2022-03",
                    end_date="Present",
                    duration_months=36,
                    bullets=[
                        "Architected distributed event-driven payment processing pipeline handling 20M+ daily events in Python and FastAPI.",
                        "Optimized PostgreSQL queries, sharding partitions and indices, reducing API p99 latency by 42% and cutting server costs by $180k/year.",
                        "Led a cross-functional squad of 6 engineers across 3 timezones, standardizing CI/CD with GitHub Actions and Docker on Kubernetes.",
                        "Mentored 4 junior engineers to senior promotions through rigorous code reviews and weekly design sessions."
                    ],
                    extracted_skills=["Python", "FastAPI", "PostgreSQL", "Kubernetes", "Docker", "Team Leadership", "GitHub Actions"]
                ),
                ExperienceItem(
                    title="Senior Software Engineer",
                    company="CloudPlatform Inc",
                    start_date="2019-06",
                    end_date="2022-02",
                    duration_months=32,
                    bullets=[
                        "Built resilient REST APIs in Python/Django backed by PostgreSQL and Redis cluster.",
                        "Migrated legacy monolithic services into Kubernetes microservices with 99.99% uptime.",
                        "Authored internal developer tooling adopted by 120+ software engineers across the organization."
                    ],
                    extracted_skills=["Python", "Django", "PostgreSQL", "Redis", "Kubernetes", "REST APIs"]
                )
            ],
            education=[
                EducationItem(degree="B.S. in Computer Science, Stanford University", year_masked=True, original_year="2018")
            ],
            external_links=[
                ExternalLinkItem(url="https://github.com/torvalds", link_type="github", verified=True, status_code=200, last_active="2026-07", metadata={"type": "user_profile", "public_repos": 48, "followers": 2100}),
                ExternalLinkItem(url="https://linkedin.com/in/alex-mercer", link_type="linkedin", verified=True, status_code=200)
            ],
            raw_text="Alex Mercer - Staff Backend Engineer. Expert in Python, PostgreSQL, Kubernetes, FastAPI. Led 6 engineers, reduced latency 42% across 20M daily requests."
        ),
        # Candidate 2: Great match for Full Stack AI Engineer
        CandidateData(
            candidate_id="cand-maya-002",
            raw_name="Maya Lin",
            anonymized_name=generate_anonymized_id("Maya Lin", "cand-maya-002"),
            contact=ContactInfo(
                email="maya.lin.ai@gmail.com",
                phone="+1 (555) 987-6543",
                location="Austin, TX",
                masked_email="ma***@gmail.com",
                masked_phone="***-***-6543",
                masked_location="[LOCATION_MASKED]"
            ),
            pii_stripped=True,
            total_experience_years=4.0,
            skills=[
                SkillItem(name="React", source="explicit_list", quantified_evidence=False),
                SkillItem(name="TypeScript", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Python", source="explicit_list", quantified_evidence=False),
                SkillItem(name="FastAPI", source="explicit_list", quantified_evidence=False),
                SkillItem(name="LLMs / Generative AI", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Vector Databases", source="explicit_list", quantified_evidence=True),
                SkillItem(name="ChromaDB", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Tailwind CSS", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Next.js", source="explicit_list", quantified_evidence=False)
            ],
            experience=[
                ExperienceItem(
                    title="Full Stack AI Engineer",
                    company="CognitiveLab AI",
                    start_date="2023-01",
                    end_date="Present",
                    duration_months=26,
                    bullets=[
                        "Built AI copilot UI using React, TypeScript, Tailwind CSS, and WebSockets serving 150k monthly active users.",
                        "Engineered RAG backend pipeline using FastAPI, LangChain, and ChromaDB vector search, improving retrieval accuracy by 35%.",
                        "Fine-tuned open-source LLMs and evaluated token latency, reducing response generation time from 2.4s to 850ms."
                    ],
                    extracted_skills=["React", "TypeScript", "Tailwind CSS", "Python", "FastAPI", "ChromaDB", "LLMs / Generative AI"]
                ),
                ExperienceItem(
                    title="Frontend Developer",
                    company="NextGen SaaS",
                    start_date="2021-06",
                    end_date="2022-12",
                    duration_months=18,
                    bullets=[
                        "Developed responsive dashboard interfaces using Next.js and TypeScript.",
                        "Increased page load speed by 28% through code splitting and asset optimization."
                    ],
                    extracted_skills=["React", "Next.js", "TypeScript", "CSS3"]
                )
            ],
            education=[
                EducationItem(degree="B.Tech in Information Technology", year_masked=True, original_year="2021")
            ],
            external_links=[
                ExternalLinkItem(url="https://github.com/shadcn", link_type="github", verified=True, status_code=200, last_active="2026-08", metadata={"type": "user_profile", "public_repos": 34, "followers": 15000}),
                ExternalLinkItem(url="https://mayalin.dev", link_type="portfolio", verified=True, status_code=200)
            ],
            raw_text="Maya Lin - Full Stack AI Engineer. React, TypeScript, Python, FastAPI, ChromaDB, LLMs. 150k MAU, reduced latency to 850ms."
        ),
        # Candidate 3: DevOps Cloud Infra Candidate
        CandidateData(
            candidate_id="cand-david-003",
            raw_name="David Vance",
            anonymized_name=generate_anonymized_id("David Vance", "cand-david-003"),
            contact=ContactInfo(
                email="david.vance.ops@outlook.com",
                phone="+1 (555) 345-6789",
                location="Seattle, WA",
                masked_email="da***@outlook.com",
                masked_phone="***-***-6789",
                masked_location="[LOCATION_MASKED]"
            ),
            pii_stripped=True,
            total_experience_years=7.0,
            skills=[
                SkillItem(name="AWS", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Kubernetes", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Terraform", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Docker", source="explicit_list", quantified_evidence=False),
                SkillItem(name="CI/CD", source="explicit_list", quantified_evidence=True),
                SkillItem(name="Linux", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Prometheus", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Team Leadership", source="inferred_from_bullet", original_text="Led platform team of 8 infrastructure engineers", quantified_evidence=True)
            ],
            experience=[
                ExperienceItem(
                    title="Lead Infrastructure Engineer",
                    company="FinTech Enterprise",
                    start_date="2021-08",
                    end_date="Present",
                    duration_months=42,
                    bullets=[
                        "Managed multi-region AWS cloud infrastructure supporting 99.995% uptime across 400+ microservices.",
                        "Wrote modular Terraform infrastructure-as-code modules managing 1,200+ AWS resources.",
                        "Reduced CI/CD build and deploy times from 45 mins to 6 mins with automated GitHub Actions workflows.",
                        "Led platform team of 8 infrastructure engineers, conducting 24/7 on-call rotations and root cause analyses."
                    ],
                    extracted_skills=["AWS", "Terraform", "Kubernetes", "CI/CD", "Docker", "Team Leadership", "Prometheus"]
                )
            ],
            education=[
                EducationItem(degree="B.S. in Electrical and Computer Engineering", year_masked=True, original_year="2017")
            ],
            external_links=[
                ExternalLinkItem(url="https://github.com/kubernetes/kubernetes", link_type="github", verified=True, status_code=200, last_active="2026-08")
            ],
            raw_text="David Vance - Lead Infrastructure Engineer. AWS, Kubernetes, Terraform, Docker, CI/CD. 99.995% uptime, reduced deploy time to 6 mins, led 8 engineers."
        ),
        # Candidate 4: Junior Candidate / Career Switcher
        CandidateData(
            candidate_id="cand-sam-004",
            raw_name="Sam Taylor",
            anonymized_name=generate_anonymized_id("Sam Taylor", "cand-sam-004"),
            contact=ContactInfo(
                email="sam.taylor.dev@mail.com",
                phone="+1 (555) 456-7890",
                location="Denver, CO",
                masked_email="sa***@mail.com",
                masked_phone="***-***-7890",
                masked_location="[LOCATION_MASKED]"
            ),
            pii_stripped=True,
            total_experience_years=1.5,
            skills=[
                SkillItem(name="Python", source="explicit_list", quantified_evidence=False),
                SkillItem(name="JavaScript", source="explicit_list", quantified_evidence=False),
                SkillItem(name="HTML5", source="explicit_list", quantified_evidence=False),
                SkillItem(name="CSS3", source="explicit_list", quantified_evidence=False),
                SkillItem(name="SQLite", source="explicit_list", quantified_evidence=False)
            ],
            experience=[
                ExperienceItem(
                    title="Junior Web Developer",
                    company="Digital Agency Co",
                    start_date="2023-06",
                    end_date="Present",
                    duration_months=18,
                    bullets=[
                        "Assisted senior developers in building client landing pages using HTML, CSS, and vanilla JavaScript.",
                        "Wrote basic Python scripts for scraping and data cleanup into SQLite databases."
                    ],
                    extracted_skills=["Python", "JavaScript", "HTML5", "CSS3", "SQLite"]
                )
            ],
            education=[
                EducationItem(degree="Certificate in Full Stack Web Development", year_masked=True, original_year="2023")
            ],
            external_links=[
                ExternalLinkItem(url="https://github.com/sam-taylor-sample", link_type="github", verified=False, status_code=404)
            ],
            raw_text="Sam Taylor - Junior Web Developer. Python, JavaScript, HTML, CSS, SQLite. Assisted building landing pages."
        ),
        # Candidate 5: Rapid Job Transition / Hopping Edge Case
        CandidateData(
            candidate_id="cand-jordan-005",
            raw_name="Jordan Reed",
            anonymized_name=generate_anonymized_id("Jordan Reed", "cand-jordan-005"),
            contact=ContactInfo(
                email="jordan.reed@freelance.org",
                phone="+1 (555) 567-8901",
                location="Chicago, IL",
                masked_email="jo***@freelance.org",
                masked_phone="***-***-8901",
                masked_location="[LOCATION_MASKED]"
            ),
            pii_stripped=True,
            total_experience_years=3.0,
            skills=[
                SkillItem(name="Python", source="explicit_list", quantified_evidence=False),
                SkillItem(name="PostgreSQL", source="explicit_list", quantified_evidence=False),
                SkillItem(name="Docker", source="explicit_list", quantified_evidence=False),
                SkillItem(name="FastAPI", source="explicit_list", quantified_evidence=False)
            ],
            experience=[
                ExperienceItem(
                    title="Backend Contractor",
                    company="Startup A",
                    start_date="2024-01",
                    end_date="2024-05",
                    duration_months=4,
                    bullets=["Built prototype REST APIs using FastAPI and PostgreSQL."],
                    extracted_skills=["Python", "FastAPI", "PostgreSQL"]
                ),
                ExperienceItem(
                    title="Software Engineer",
                    company="Startup B",
                    start_date="2023-07",
                    end_date="2023-12",
                    duration_months=5,
                    bullets=["Dockerized microservices and fixed bugs."],
                    extracted_skills=["Docker", "Python"]
                ),
                ExperienceItem(
                    title="Junior Developer",
                    company="Startup C",
                    start_date="2023-01",
                    end_date="2023-06",
                    duration_months=5,
                    bullets=["Maintained internal database scripts."],
                    extracted_skills=["PostgreSQL", "Python"]
                )
            ],
            education=[
                EducationItem(degree="B.S. in Computer Science", year_masked=True, original_year="2022")
            ],
            external_links=[],
            raw_text="Jordan Reed - Backend Developer. Python, PostgreSQL, Docker, FastAPI. 3 short contractor stints."
        )
    ]
    enriched = [enrich_candidate_with_evidence(c) for c in cands]
    return enriched
