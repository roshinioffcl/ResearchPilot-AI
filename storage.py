import os
from pathlib import Path

# Local default: ./data
# Render: set RESEARCHPILOT_DATA_DIR=/var/data
DATA_DIR = Path(os.getenv("RESEARCHPILOT_DATA_DIR", "data"))

DOCUMENTS_DIR = DATA_DIR / "documents"
PROCESSED_DIR = DATA_DIR / "processed"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Ensure all required directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)