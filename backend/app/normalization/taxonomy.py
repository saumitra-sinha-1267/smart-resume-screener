import re
from typing import List, Tuple, Dict, Set, Optional

SKILL_SYNONYMS: Dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "golang": "Go",
    "go lang": "Go",
    "go": "Go",
    "rust": "Rust",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "r": "R",
    "sql": "SQL",
    "bash": "Bash / Shell",
    "shell": "Bash / Shell",
    "powershell": "PowerShell",
    
    # Frontend & Mobile
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react native": "React Native",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "svelte": "Svelte",
    "sveltekit": "Svelte",
    "redux": "Redux",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "sass": "Sass/SCSS",
    "scss": "Sass/SCSS",
    "flutter": "Flutter",
    "ios": "iOS Development",
    "android": "Android Development",
    
    # Backend & Frameworks
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "nestjs": "NestJS",
    "nest.js": "NestJS",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "laravel": "Laravel",
    "asp.net": "ASP.NET Core",
    "asp.net core": "ASP.NET Core",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "restful": "REST APIs",
    "grpc": "gRPC",
    "microservices": "Microservices",
    "websockets": "WebSockets",
    "event-driven": "Event-Driven Architecture",
    
    # Databases & Storage
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Apache Cassandra",
    "dynamodb": "DynamoDB",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "neo4j": "Neo4j",
    "couchdb": "CouchDB",
    "clickhouse": "ClickHouse",
    "snowflake": "Snowflake",
    "bigquery": "BigQuery",
    
    # Cloud, DevOps & Infrastructure
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "helm": "Helm",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "jenkins": "Jenkins",
    "linux": "Linux",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "nginx": "Nginx",
    "kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",
    "serverless": "Serverless / AWS Lambda",
    "aws lambda": "Serverless / AWS Lambda",
    
    # Data Science, AI & ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "llm": "LLMs / Generative AI",
    "llms": "LLMs / Generative AI",
    "generative ai": "LLMs / Generative AI",
    "genai": "LLMs / Generative AI",
    "rag": "RAG (Retrieval-Augmented Generation)",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "chromadb": "ChromaDB",
    "vector database": "Vector Databases",
    "vector db": "Vector Databases",
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "qdrant": "Qdrant",
    "milvus": "Milvus",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spark": "Apache Spark",
    "pyspark": "Apache Spark",
    "airflow": "Apache Airflow",
    "dbt": "dbt",
    "statistics": "Statistics",
    "statistical analysis": "Statistics",
    "statistical modeling": "Statistics",
    "stats": "Statistics",
    "data visualization": "Data Visualization",
    "data visualisation": "Data Visualization",
    "visualization": "Data Visualization",
    "dataviz": "Data Visualization",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "plotly": "Plotly",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "streamlit": "Streamlit",
    "excel": "Microsoft Excel",
    "data analysis": "Data Analysis",
    "exploratory data analysis": "Exploratory Data Analysis",
    "eda": "Exploratory Data Analysis",
    
    # Leadership & Soft Skills
    "leadership": "Team Leadership",
    "team lead": "Team Leadership",
    "tech lead": "Tech Leadership",
    "mentoring": "Mentorship & Coaching",
    "mentorship": "Mentorship & Coaching",
    "agile": "Agile / Scrum",
    "scrum": "Agile / Scrum",
    "kanban": "Agile / Scrum",
    "project management": "Project Management",
    "stakeholder management": "Stakeholder Management",
    "cross-functional": "Cross-Functional Collaboration",
    "system design": "System Design & Architecture",
    "code review": "Code Review & Quality Assurance",
    "performance optimization": "Performance Optimization"
}

BULLET_ACTION_PATTERNS: List[Tuple[str, str, str]] = [
    (
        r"\b(led|managed|guided|supervised|mentored)\s+(?:a\s+)?(?:[\w-]+\s+){0,3}(squad|team|group|pod|engineers|developers)\b",
        "Team Leadership",
        "Directly mentions leading or managing a team/engineers"
    ),
    (
        r"\b(managed\s+\d+\s+direct\s+reports|reports\s+to)\b",
        "Team Leadership",
        "Manages direct reports"
    ),
    (
        r"\b(spearheaded|championed|architected|designed)\s+(the\s+)?(migration|transition|system|architecture|platform)\b",
        "System Design & Architecture",
        "Led system design or platform architecture"
    ),
    (
        r"\b(optimized|reduced|improved|boosted|accelerated|cut)\s+.*(latency|throughput|response time|query time|performance|load time)\b",
        "Performance Optimization",
        "Delivered measurable performance and latency improvements"
    ),
    (
        r"\b(automated|built|designed|implemented)\s+(a\s+)?(ci/cd|pipeline|deployment|build|release\s+workflow)\b",
        "CI/CD",
        "Engineered automated build or deployment pipelines"
    ),
    (
        r"\b(containerized|dockerized|deployed\s+on\s+kubernetes|k8s\s+cluster|helm\s+charts)\b",
        "Kubernetes",
        "Worked with containerization and orchestration"
    ),
    (
        r"\b(cross-functional|collaborated\s+with\s+product|stakeholders|designers)\b",
        "Cross-Functional Collaboration",
        "Collaborated across product and engineering disciplines"
    ),
    (
        r"\b(conducted\s+code\s+reviews|standardized\s+code\s+quality|unit\s+tests|integration\s+tests|test\s+coverage)\b",
        "Code Review & Quality Assurance",
        "Maintained code quality and testing practices"
    ),
    (
        r"\b(fine-tuned|prompt\s+engineering|rag|retrieval\s+augmented|vector\s+embeddings|embeddings)\b",
        "LLMs / Generative AI",
        "Engineered LLM, RAG, or embedding workflows"
    ),
    (
        r"\b(indexed|sharded|partitioned|database\s+optimization|slow\s+queries|normalized)\b",
        "Database Optimization",
        "Engineered database tuning and indexing strategies"
    ),
    (
        r"\b(visualized|dashboard|dashboards|plotly|tableau|power\s*bi|matplotlib|seaborn|streamlit|interactive\s+charts|plots)\b",
        "Data Visualization",
        "Engineered visual dashboards and reporting tools"
    ),
    (
        r"\b(hypothesis\s+testing|statistical|regression\s+analysis|p-value|a/b\s+test|significance|variance|anova)\b",
        "Statistics",
        "Applied statistical modeling or hypothesis testing"
    )
]

# Academic degree disciplines mapping
EXACT_DEGREE_FIELDS = [
    r"\b(?:computer\s+science|software\s+engineering|data\s+science|artificial\s+intelligence|machine\s+learning|information\s+technology|statistics|mathematics|applied\s+mathematics)\b",
    r"\b(?:cs|it|cse|ai|ds)\b"
]

RELATED_DEGREE_FIELDS = [
    r"\b(?:electronics|electrical|ece|eee|telecommunication|information\s+systems|physics|computational\s+biology|mechanical|civil|chemical|engineering)\b",
    r"\b(?:b\.?tech|b\.?e\.?|m\.?tech|m\.?e\.?)\b"
]

def classify_degree_alignment(degree_text: str) -> Tuple[str, str, str]:
    """
    Evaluates degree relevance against STEM / CS requirements.
    Returns (status: 'MATCHED' | 'PARTIAL' | 'MISSING', strength: 'STRONG' | 'MEDIUM' | 'WEAK' | 'NONE', reasoning: str)
    """
    if not degree_text or degree_text.strip().lower() in ["", "not specified", "unlisted"]:
        return "MISSING", "NONE", "No academic degree credential evidenced in resume."

    deg_lower = degree_text.lower()

    # Exact Match Check
    for pat in EXACT_DEGREE_FIELDS:
        if re.search(pat, deg_lower):
            return "MATCHED", "STRONG", f"Exact academic discipline match: {degree_text} satisfies core requirements."

    # Related Technical Field Check (e.g. ECE / Electronics / Electrical / General Engineering)
    for pat in RELATED_DEGREE_FIELDS:
        if re.search(pat, deg_lower):
            return "PARTIAL", "MEDIUM", f"Related technical engineering discipline: {degree_text} partially aligns with core requirements."

    # Non-technical / general field
    return "PARTIAL", "WEAK", f"Degree listed ({degree_text}) does not directly match core computing/data disciplines."

def normalize_skill(skill_raw: str) -> str:
    cleaned = skill_raw.strip().lower()
    cleaned = re.sub(r"[\(\)\[\],]", "", cleaned).strip()
    if cleaned in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned]
    words = cleaned.split()
    if len(words) == 1 and cleaned in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned]
    return skill_raw.strip().title()

def infer_skills_from_bullet(bullet: str) -> List[Tuple[str, str]]:
    inferred: List[Tuple[str, str]] = []
    bullet_lower = bullet.lower()
    for pattern, skill, reason in BULLET_ACTION_PATTERNS:
        if re.search(pattern, bullet_lower):
            inferred.append((skill, reason))
    return inferred

def extract_explicit_skills(text: str) -> List[str]:
    found: Set[str] = set()
    text_lower = f" {text.lower()} "
    for alias, canonical in SKILL_SYNONYMS.items():
        pattern = r"(?<![a-zA-Z0-9_])" + re.escape(alias) + r"(?![a-zA-Z0-9_])"
        if re.search(pattern, text_lower):
            found.add(canonical)
    return sorted(list(found))
