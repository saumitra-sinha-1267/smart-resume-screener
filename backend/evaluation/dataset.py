from typing import List, Dict
from app.normalization.schema_models import CandidateData, SkillItem, ExperienceItem, EducationItem, ExternalLinkItem, JobData

BENCHMARK_JOB_BACKEND = JobData(
    job_id="eval-job-backend-001",
    title="Senior Backend Engineer",
    department="Core Infrastructure",
    seniority="Senior",
    min_experience_years=5.0,
    required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "Microservices"],
    preferred_skills=["Go", "Apache Kafka", "Redis", "AWS", "CI/CD"],
    education_requirements=["B.S. in Computer Science or equivalent"],
    raw_description="""
    Job Title: Senior Backend Engineer
    Department: Core Infrastructure
    Seniority: Senior
    Minimum Experience: 5+ years
    
    Required:
    - 5+ years of experience with Python, FastAPI, and PostgreSQL.
    - Deep hands-on experience with Docker, Kubernetes, and Microservices.
    
    Preferred:
    - Experience with Go, Apache Kafka, Redis, and AWS.
    - Strong history of distributed systems optimization and CI/CD pipelines.
    """
)

BENCHMARK_JOB_FULLSTACK = JobData(
    job_id="eval-job-fullstack-002",
    title="Senior Fullstack React Engineer",
    department="Product Engineering",
    seniority="Senior",
    min_experience_years=4.0,
    required_skills=["React", "TypeScript", "Node.js", "GraphQL", "Tailwind CSS"],
    preferred_skills=["Next.js", "PostgreSQL", "AWS", "Jest"],
    raw_description="Senior Fullstack React and TypeScript developer with Node.js and GraphQL."
)

BENCHMARK_CANDIDATES: List[CandidateData] = [
    # 1. Ideal Backend Match (Grade 3)
    CandidateData(
        candidate_id="eval-cand-001",
        raw_name="Marcus Vance",
        anonymized_name="Candidate #EVAL01",
        total_experience_years=6.5,
        skills=[
            SkillItem(name="Python", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="FastAPI", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="PostgreSQL", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="Docker", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Kubernetes", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="Microservices", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Apache Kafka", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="Redis", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Senior Backend Engineer",
                company="Apex Scale Systems",
                start_date="2021",
                end_date="Present",
                bullets=[
                    "Architected high-throughput Python FastAPI microservices handling 45k req/sec with PostgreSQL.",
                    "Optimized database query latency by 42% across 20M daily queries using connection pooling.",
                    "Deployed Kubernetes clusters on AWS managing 80+ microservices."
                ],
                extracted_skills=["Python", "FastAPI", "PostgreSQL", "Kubernetes", "AWS"]
            ),
            ExperienceItem(
                title="Backend Developer",
                company="Nexus Tech",
                start_date="2018",
                end_date="2021",
                bullets=[
                    "Built asynchronous event streaming pipeline using Apache Kafka and Redis.",
                    "Implemented Docker containerization for 15 internal services."
                ],
                extracted_skills=["Apache Kafka", "Redis", "Docker", "Python"]
            )
        ],
        education=[EducationItem(degree="B.S. in Computer Science", institution="State Tech University", year_masked=True)],
        external_links=[ExternalLinkItem(url="https://github.com/marcusv-dev", link_type="github", verified=True)]
    ),

    # 2. Strong Backend Match (Grade 3)
    CandidateData(
        candidate_id="eval-cand-002",
        raw_name="Sarah Chen",
        anonymized_name="Candidate #EVAL02",
        total_experience_years=5.5,
        skills=[
            SkillItem(name="Python", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="FastAPI", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="PostgreSQL", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="Docker", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Kubernetes", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Microservices", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Go", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Lead Infrastructure Engineer",
                company="CloudStream Labs",
                start_date="2020",
                end_date="Present",
                bullets=[
                    "Engineered Python and Go distributed backend services reducing API response times by 35%.",
                    "Managed relational PostgreSQL schemas and index optimization.",
                    "Configured Docker containers and Kubernetes deployments."
                ],
                extracted_skills=["Python", "Go", "PostgreSQL", "Docker", "Kubernetes"]
            )
        ],
        education=[EducationItem(degree="M.S. in Software Engineering", institution="Polytechnic Institute", year_masked=True)],
        external_links=[ExternalLinkItem(url="https://github.com/schen-infra", link_type="github", verified=True)]
    ),

    # 3. Solid Backend Match (Grade 2)
    CandidateData(
        candidate_id="eval-cand-003",
        raw_name="David Okafor",
        anonymized_name="Candidate #EVAL03",
        total_experience_years=5.0,
        skills=[
            SkillItem(name="Python", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Django", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="FastAPI", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="PostgreSQL", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Docker", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Microservices", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Software Engineer",
                company="Fintech Dynamics",
                start_date="2019",
                end_date="Present",
                bullets=[
                    "Developed backend RESTful APIs using Python, Django, and FastAPI.",
                    "Integrated PostgreSQL database models and Dockerized application services."
                ],
                extracted_skills=["Python", "Django", "FastAPI", "PostgreSQL", "Docker"]
            )
        ],
        education=[EducationItem(degree="B.S. in Information Systems", institution="University College", year_masked=True)],
        external_links=[]
    ),

    # 4. Adequate Backend Match (Grade 2)
    CandidateData(
        candidate_id="eval-cand-004",
        raw_name="Elena Rostova",
        anonymized_name="Candidate #EVAL04",
        total_experience_years=4.5,
        skills=[
            SkillItem(name="Python", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="PostgreSQL", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Docker", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Microservices", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Redis", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Backend Developer",
                company="DataMesh Global",
                start_date="2020",
                end_date="Present",
                bullets=[
                    "Built microservices with Python and PostgreSQL handling 10k daily transactions.",
                    "Improved Redis caching layer reducing database reads by 50%."
                ],
                extracted_skills=["Python", "PostgreSQL", "Redis", "Microservices"]
            )
        ],
        education=[EducationItem(degree="B.S. in Computer Engineering", institution="National Tech University", year_masked=True)],
        external_links=[]
    ),

    # 5. Fullstack Match (Grade 1 for Backend)
    CandidateData(
        candidate_id="eval-cand-005",
        raw_name="Maya Lin",
        anonymized_name="Candidate #EVAL05",
        total_experience_years=5.0,
        skills=[
            SkillItem(name="React", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="TypeScript", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="Node.js", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="GraphQL", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Tailwind CSS", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="PostgreSQL", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Senior Fullstack Developer",
                company="OmniUI Solutions",
                start_date="2019",
                end_date="Present",
                bullets=[
                    "Led frontend development with React, TypeScript, and Tailwind CSS boosting page speed by 40%.",
                    "Architected Node.js and GraphQL backend services interfacing with PostgreSQL."
                ],
                extracted_skills=["React", "TypeScript", "Node.js", "GraphQL", "Tailwind CSS", "PostgreSQL"]
            )
        ],
        education=[EducationItem(degree="B.S. in Computer Science", institution="State University", year_masked=True)],
        external_links=[ExternalLinkItem(url="https://github.com/mayalin-dev", link_type="github", verified=True)]
    ),

    # 6. Junior Backend Developer (Grade 1)
    CandidateData(
        candidate_id="eval-cand-006",
        raw_name="Lucas Meyer",
        anonymized_name="Candidate #EVAL06",
        total_experience_years=1.5,
        skills=[
            SkillItem(name="Python", source="explicit_list", evidence_strength="WEAK"),
            SkillItem(name="FastAPI", source="explicit_list", evidence_strength="WEAK"),
            SkillItem(name="PostgreSQL", source="explicit_list", evidence_strength="WEAK")
        ],
        experience=[
            ExperienceItem(
                title="Junior Python Developer",
                company="Startup Hub",
                start_date="2023",
                end_date="Present",
                bullets=[
                    "Assisted in maintaining FastAPI routes and fixing PostgreSQL queries.",
                    "Participated in sprint planning."
                ],
                extracted_skills=["Python", "FastAPI", "PostgreSQL"]
            )
        ],
        education=[EducationItem(degree="B.S. in Computer Science", institution="City College", year_masked=True)],
        external_links=[]
    ),

    # 7. Unrelated Frontend Specialist (Grade 0)
    CandidateData(
        candidate_id="eval-cand-007",
        raw_name="Chloe Dupuis",
        anonymized_name="Candidate #EVAL07",
        total_experience_years=4.0,
        skills=[
            SkillItem(name="React", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="TypeScript", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="CSS3", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="HTML5", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Redux", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Frontend Developer",
                company="PixelWorks Studio",
                start_date="2020",
                end_date="Present",
                bullets=[
                    "Developed web UI layouts using React and Redux.",
                    "Converted Figma prototypes to responsive CSS3."
                ],
                extracted_skills=["React", "TypeScript", "CSS3", "HTML5", "Redux"]
            )
        ],
        education=[EducationItem(degree="B.A. in Digital Arts", institution="Design Academy", year_masked=True)],
        external_links=[]
    ),

    # 8. Unrelated Mobile Developer (Grade 0)
    CandidateData(
        candidate_id="eval-cand-008",
        raw_name="Carlos Mendez",
        anonymized_name="Candidate #EVAL08",
        total_experience_years=5.0,
        skills=[
            SkillItem(name="Swift", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="iOS Development", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Kotlin", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Android Development", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Mobile App Engineer",
                company="AppNation",
                start_date="2019",
                end_date="Present",
                bullets=[
                    "Built native iOS applications in Swift and Android apps in Kotlin.",
                    "Published 4 apps to Apple App Store."
                ],
                extracted_skills=["Swift", "iOS Development", "Kotlin"]
            )
        ],
        education=[EducationItem(degree="B.S. in Computer Science", institution="Tech University", year_masked=True)],
        external_links=[]
    ),

    # 9. Non-Technical / Quality Assurance (Grade 0)
    CandidateData(
        candidate_id="eval-cand-009",
        raw_name="Amira Patel",
        anonymized_name="Candidate #EVAL09",
        total_experience_years=3.0,
        skills=[
            SkillItem(name="Agile / Scrum", source="explicit_list", evidence_strength="WEAK"),
            SkillItem(name="Project Management", source="explicit_list", evidence_strength="WEAK"),
            SkillItem(name="Manual Testing", source="explicit_list", evidence_strength="WEAK")
        ],
        experience=[
            ExperienceItem(
                title="QA Analyst",
                company="Quality First",
                start_date="2021",
                end_date="Present",
                bullets=[
                    "Executed manual test cases for web applications.",
                    "Logged bug tickets in Jira and coordinated with developers."
                ],
                extracted_skills=["Agile / Scrum", "Project Management"]
            )
        ],
        education=[EducationItem(degree="B.A. in Communications", institution="Metropolitan College", year_masked=True)],
        external_links=[]
    ),

    # 10. Data Scientist / ML Engineer (Grade 1)
    CandidateData(
        candidate_id="eval-cand-010",
        raw_name="Dr. Julian Ross",
        anonymized_name="Candidate #EVAL10",
        total_experience_years=6.0,
        skills=[
            SkillItem(name="Python", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="PyTorch", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Machine Learning", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="Pandas", source="explicit_list", evidence_strength="MEDIUM"),
            SkillItem(name="PostgreSQL", source="explicit_list", evidence_strength="WEAK")
        ],
        experience=[
            ExperienceItem(
                title="Senior Data Scientist",
                company="Cortex Insights",
                start_date="2018",
                end_date="Present",
                bullets=[
                    "Trained neural network models using Python and PyTorch achieving 94% accuracy.",
                    "Queried PostgreSQL tables and analyzed datasets with Pandas."
                ],
                extracted_skills=["Python", "PyTorch", "Machine Learning", "PostgreSQL"]
            )
        ],
        education=[EducationItem(degree="Ph.D. in Computational Statistics", institution="National Research Univ", year_masked=True)],
        external_links=[]
    )
]

GROUND_TRUTH_BACKEND_RELEVANCE: Dict[str, int] = {
    "eval-cand-001": 3,
    "eval-cand-002": 3,
    "eval-cand-003": 2,
    "eval-cand-004": 2,
    "eval-cand-005": 1,
    "eval-cand-006": 1,
    "eval-cand-007": 0,
    "eval-cand-008": 0,
    "eval-cand-009": 0,
    "eval-cand-010": 1,
}
