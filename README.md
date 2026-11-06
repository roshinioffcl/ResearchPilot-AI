# 🔬 ResearchPilot AI

An AI-powered research assistant that helps users explore, understand, and compare research papers using Retrieval-Augmented Generation (RAG).

## 🎯 Project Goal

ResearchPilot AI aims to make academic research easier by allowing users to upload research papers, ask questions, retrieve relevant information, and receive answers grounded in the original documents with page-level citations.

## 🛠️ Tech Stack

**Frontend**
- React
- TypeScript
- Vite

**Backend**
- Python
- FastAPI

**AI & RAG**
- PyMuPDF
- Sentence Transformers
- FAISS / ChromaDB
- LLM API

**Tools**
- Git & GitHub
- VS Code

## ✨ Planned Features

- Upload and process multiple research papers.
- Extract text while preserving page numbers.
- Generate embeddings for semantic search.
- Retrieve relevant passages from documents.
- Generate context-grounded AI answers.
- Provide page-level source citations.
- Compare multiple research papers.
- Evaluate retrieval quality and answer faithfulness.

## 🚧 Development Status

Currently in Milestone 1: Python environment, initial Streamlit interface, and GitHub setup.

The remaining features will be implemented progressively.

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/roshinioffcl/ResearchPilot-AI.git
cd ResearchPilot-AI
```

### 2. Create a virtual environment

```bash
py -3.12 -m venv .venv
```

### 3. Activate the environment (Windows CMD)

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 📌 Project Roadmap

1. Python and Project Setup
2. PDF Processing
3. Embeddings
4. Vector Database
5. RAG Pipeline
6. Backend and Frontend
7. Evaluation and Deployment

## 👩‍💻 Author

Roshini

---

*ResearchPilot AI — Turning research papers into conversations.*