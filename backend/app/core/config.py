import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BACKEND_DIR, ".env"))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
DB_PATH = os.path.join(DATA_DIR, "screener.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "Smart Resume Screener"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DB_PATH: str = (os.getenv("DATABASE_PATH") or "").strip() or DB_PATH
    UPLOADS_DIR: str = (os.getenv("UPLOADS_DIR") or "").strip() or UPLOADS_DIR
    GEMINI_API_KEY: str = (os.getenv("GEMINI_API_KEY") or "").strip()
    OPENAI_API_KEY: str = (os.getenv("OPENAI_API_KEY") or "").strip()
    GITHUB_TOKEN: str = (os.getenv("GITHUB_TOKEN") or "").strip()
    TOP_N_FILTER: int = int((os.getenv("TOP_N_FILTER") or "").strip() or "15")
    ENABLE_LINK_CHECK: bool = (os.getenv("ENABLE_LINK_CHECK") or "true").strip().lower() == "true"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.65

settings = Settings()
