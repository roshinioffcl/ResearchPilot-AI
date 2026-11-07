import traceback
from pathlib import Path
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from storage import DOCUMENTS_DIR

from retriever import retrieve_chunks
from answer_generator import generate_answer, rewrite_question
from pdf_processor import extract_pages
from document_ingestor import index_documents, delete_document_from_index
from document_manager import register_document, get_documents, remove_document_record


app = FastAPI(
    title="ResearchPilot AI",
    description="AI-powered research assistant",
    version="1.0.0"
)

allowed_origins = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RELEVANCE_THRESHOLD = 1.2


class ChatRequest(BaseModel):
    question: str
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


@app.get("/")
def home():
    return {"message": "ResearchPilot AI backend is running!"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResearchPilot AI"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        return {"answer": "Please enter a question.", "sources": []}

    history = request.conversation_history
    search_query = rewrite_question(question, history)
    chunks = retrieve_chunks(search_query)

    if not chunks or chunks[0]["distance"] > RELEVANCE_THRESHOLD:
        return {
            "answer": "I couldn't find sufficiently relevant information in your documents.",
            "sources": []
        }

    answer = generate_answer(search_query, chunks, history)

    sources = [
        {
            "document": chunk["document"],
            "page": chunk["page"]
        }
        for chunk in chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    pdf_bytes = await file.read()

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")

    try:
        pages = extract_pages(pdf_bytes, filename)
        chunk_count = index_documents(pages)

        documents_path = DOCUMENTS_DIR
        documents_path.mkdir(parents=True, exist_ok=True)

        pdf_path = documents_path / filename
        pdf_path.write_bytes(pdf_bytes)

        register_document(
            filename,
            page_count=len(pages),
            chunk_count=chunk_count
        )

        return {
            "message": "Document uploaded and indexed successfully.",
            "document": filename,
            "pages": len(pages),
            "chunks": chunk_count
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        traceback.print_exc()  # prints the real error in the terminal
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {error}"
        ) from error

    finally:
        await file.close()


@app.get("/documents")
def list_documents():
    return get_documents()


@app.delete("/documents/{filename}")
def delete_document(filename: str):
    filename = Path(filename).name

    documents = get_documents()

    if filename not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")

    delete_document_from_index(filename)
    remove_document_record(filename)

    return {
        "message": "Document deleted successfully.",
        "document": filename
    }