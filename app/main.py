from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.ingest import load_documents
from app.chunking import fixed_chunk
from app.embedding import embed_texts
from app.vector_store import VectorStore
from app.api import create_routes

app = FastAPI(
    title="Document Intelligence System",
    description="HR Document RAG Assistant API",
    version="1.0.0"
)

# =====================================================
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Frontend"
DATA_DIR = BASE_DIR / "data"

# =====================================================
# APP STATE
# =====================================================
app.state.vector_store = None

# =====================================================
# SERVE FRONTEND
# =====================================================
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse(
            content={"error": "index.html not found in Frontend folder"},
            status_code=404
        )

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        ico_path = FRONTEND_DIR / "favicon.ico"
        if ico_path.exists():
            return FileResponse(str(ico_path))
        return Response(status_code=204)

    print(f"✅ Frontend served from: {FRONTEND_DIR}")
else:
    print(f"⚠️ Frontend folder not found at: {FRONTEND_DIR}")

# =====================================================
# STARTUP: LOAD DOCS + BUILD VECTOR STORE
# =====================================================
@app.on_event("startup")
def startup_event():
    try:
        print("📦 Loading documents from data folder...")

        if not DATA_DIR.exists():
            print(f"⚠️ Data folder not found at: {DATA_DIR}")
            app.state.vector_store = None
            return

        docs = load_documents(str(DATA_DIR))

        if not docs:
            print("⚠️ No documents found in data folder.")
            app.state.vector_store = None
            return

        all_chunks = []
        sources = []

        for doc in docs:
            text = doc.get("text", "")
            source = doc.get("source", "unknown")

            if not text or not text.strip():
                continue

            chunks = fixed_chunk(text.strip())

            if not chunks:
                continue

            all_chunks.extend(chunks)
            sources.extend([source] * len(chunks))

        print(f"✅ Total documents loaded: {len(docs)}")
        print(f"✅ Total chunks created: {len(all_chunks)}")

        if not all_chunks:
            print("⚠️ No chunks created.")
            app.state.vector_store = None
            return

        print("🧠 Creating embeddings...")
        embeddings = embed_texts(all_chunks)

        if embeddings is None:
            print("⚠️ Embeddings are None.")
            app.state.vector_store = None
            return

        if hasattr(embeddings, "shape"):
            if embeddings.shape[0] == 0:
                print("⚠️ Embeddings array is empty.")
                app.state.vector_store = None
                return
            dimension = int(embeddings.shape[1])
        else:
            if len(embeddings) == 0:
                print("⚠️ Embeddings list is empty.")
                app.state.vector_store = None
                return
            dimension = len(embeddings[0])

        print(f"✅ Embedding dimension detected: {dimension}")

        vector_store = VectorStore(dimension)
        vector_store.add(embeddings, all_chunks, sources)

        app.state.vector_store = vector_store

        print("✅ Vector store ready!")
        print("🚀 FastAPI Application Ready!")

    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
        app.state.vector_store = None

# =====================================================
# API ROUTES
# =====================================================
app.include_router(create_routes())
