from fastapi import APIRouter
from app.schemas import AskRequest

def create_routes(vector_store, embed_texts):

    router = APIRouter()

    @router.post("/ask")
    def ask_question(request: AskRequest):

        query_embedding = embed_texts([request.question])[0]

        results = vector_store.search(query_embedding)

        return {
            "answer": results[0]["text"] if results else "No answer found",
            "confidence": "High",
            "source_documents": [
                r["source"] for r in results
            ],
            "similarity_score":
                results[0]["score"] if results else 0
        }

    return router
