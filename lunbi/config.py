import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# File paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_PATH = PROJECT_ROOT / "data" / "articles"
CHROMA_PATH = PROJECT_ROOT / "chroma"
# Model settings
EMBEDDING_MODEL = "text-embedding-3-small"
MODEL = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.3
# Database
POSTGRES_USER = os.getenv("POSTGRES_USER", "lunbi")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "lunbi")
POSTGRES_DB = os.getenv("POSTGRES_DB", "lunbi")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
