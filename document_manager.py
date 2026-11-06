
import json
from pathlib import Path
from datetime import datetime
from storage import DOCUMENTS_DIR, PROCESSED_DIR

REGISTRY_PATH = PROCESSED_DIR / "document_registry.json"


def load_registry():

    if not REGISTRY_PATH.exists():
        return {}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_registry(registry):

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as file:
        json.dump(registry, file, indent=4, ensure_ascii=False)


def register_document(filename, page_count, chunk_count):

    registry = load_registry()

    registry[filename] = {
        "pages": page_count,
        "chunks": chunk_count,
        "indexed_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    save_registry(registry)


def get_documents():

    return load_registry()

def remove_document_record(filename):

    registry = load_registry()

    if filename not in registry:
        return False

    del registry[filename]

    save_registry(registry)

    # Remove the original PDF
    pdf_path = DOCUMENTS_DIR / filename

    if pdf_path.exists():
        pdf_path.unlink()

    return True
