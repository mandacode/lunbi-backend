from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "articles"
CHROMA_PATH = BASE_DIR / "chroma"
# Model settings
EMBEDDING_MODEL = "text-embedding-3-small"
MODEL = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.3