# Document Intelligence RAG System

A Retrieval-Augmented Generation (RAG) based document question-answering
system built using FastAPI, LangChain, ChromaDB, and Groq LLM.

This project allows users to ingest documents, create embeddings,
retrieve relevant context, and generate AI-powered answers.

------------------------------------------------------------

## Features

- Document ingestion and chunking
- Vector embeddings using ChromaDB
- Semantic search and retrieval
- LLM-based answer generation
- FastAPI REST API
- Modular project structure

------------------------------------------------------------

## Project Structure

document_intelligence/
│
├── app/
│   ├── api.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── generator.py
│   ├── guardrails.py
│   ├── ingest.py
│   ├── main.py
│   ├── retriever.py
│   ├── schemas.py
│   └── vector_store.py
│
├── data/
│   ├── client_x_requirements.txt
│   ├── screening_checklist_python.txt
│   ├── compliance_policy.txt
│   ├── rate_card_2026.txt
│   └── placement_checklist.txt
│
├── requirements.txt
└── README.md

------------------------------------------------------------

## Setup Instructions

### 1. Create Virtual Environment

Windows:
python -m venv .venv
.venv\Scripts\activate

Mac/Linux:
python -m venv .venv
source .venv/bin/activate

------------------------------------------------------------

### 2. Install Dependencies

pip install -r requirements.txt

------------------------------------------------------------

### 3. Environment Variables

Create a file named `.env` in the project root:

GROQ_API_KEY=your_api_key_here

------------------------------------------------------------

### 4. Run the Application

uvicorn document_intelligence.app.main:app --reload

Open in browser:
http://127.0.0.1:8000/docs

------------------------------------------------------------

## How It Works

1. Add documents to the data/ folder.
2. Run ingestion to create embeddings.
3. Ask questions through API endpoints.
4. The system retrieves relevant content and generates answers.

------------------------------------------------------------

## Technologies

- Python
- FastAPI
- LangChain
- ChromaDB
- Groq LLM

------------------------------------------------------------

## Notes

- Keep documents organized inside the data folder.
- Update paths in ingest.py if you change folder structure.
- Store API keys securely using .env file.

------------------------------------------------------------

## License

Educational and internal project use.
