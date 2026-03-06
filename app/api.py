from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict, Any, List

from app.embedding import embed_texts


class AskRequest(BaseModel):
    question: str


def compute_confidence(top_score: float, second_score: float = 0.0) -> float:
    """
    Confidence derived from retrieval:
    - Higher top_score => higher confidence
    - Larger gap between top and second => higher confidence
    Range: 0..1
    """
    gap = max(0.0, top_score - second_score)
    conf = (0.8 * top_score) + (0.2 * min(gap * 2, 1.0))
    return max(0.0, min(conf, 1.0))


def create_routes():
    router = APIRouter()

    TOP_K = 6
    NOT_FOUND_THRESHOLD = 0.35
    FOUND_THRESHOLD = 0.50
    MAX_CONTEXT_CHARS = 3200

    @router.get("/health")
    async def health():
        return {"status": "ok"}

    @router.post("/ask")
    async def ask(req: AskRequest, request: Request) -> Dict[str, Any]:
        try:
            vector_store = request.app.state.vector_store

            if vector_store is None:
                return {
                    "found": False,
                    "answer": "Vector store is not ready.",
                    "confidence": 0.0,
                    "top_similarity": 0.0,
                    "matches": [],
                    "source_documents": []
                }

            question = (req.question or "").strip()
            if not question:
                return {
                    "found": False,
                    "answer": "Information not found.",
                    "confidence": 0.0,
                    "top_similarity": 0.0,
                    "matches": [],
                    "source_documents": []
                }

            query_embeddings = embed_texts([question])

            if query_embeddings is None or len(query_embeddings) == 0:
                return {
                    "found": False,
                    "answer": "Failed to create query embedding.",
                    "confidence": 0.0,
                    "top_similarity": 0.0,
                    "matches": [],
                    "source_documents": []
                }

            q_emb = query_embeddings[0]
            results = vector_store.search(q_emb, top_k=TOP_K)

            if not results:
                return {
                    "found": False,
                    "answer": "Information not found.",
                    "confidence": 0.0,
                    "top_similarity": 0.0,
                    "matches": [],
                    "source_documents": []
                }

            top_score = float(results[0].get("score", 0.0))
            second_score = float(results[1].get("score", 0.0)) if len(results) > 1 else 0.0

            matches_ui: List[Dict[str, Any]] = []
            for r in results[:5]:
                snippet = (r.get("text", "") or "").strip()
                if len(snippet) > 420:
                    snippet = snippet[:420] + "..."

                matches_ui.append({
                    "source": r.get("source", "unknown"),
                    "score": round(float(r.get("score", 0.0)), 4),
                    "snippet": snippet
                })

            if top_score < NOT_FOUND_THRESHOLD:
                return {
                    "found": False,
                    "answer": "Information not found.",
                    "confidence": 0.0,
                    "top_similarity": round(top_score, 4),
                    "matches": matches_ui,
                    "source_documents": list(dict.fromkeys([m["source"] for m in matches_ui]))
                }

            context_parts: List[str] = []
            used_sources: List[str] = []
            used_chars = 0

            for r in results:
                score = float(r.get("score", 0.0))
                if score < NOT_FOUND_THRESHOLD:
                    continue

                chunk = (r.get("text", "") or "").strip()
                source = r.get("source", "unknown")

                if not chunk:
                    continue

                if used_chars + len(chunk) > MAX_CONTEXT_CHARS:
                    break

                context_parts.append(f"[SOURCE: {source} | sim={score:.3f}]\n{chunk}")
                used_sources.append(source)
                used_chars += len(chunk)

            answer = (results[0].get("text", "") or "").strip()
            confidence = compute_confidence(top_score, second_score)
            found = top_score >= FOUND_THRESHOLD

            return {
                "found": found,
                "answer": answer if found else f"(Low match) Best related info found:\n\n{answer}",
                "confidence": round(float(confidence), 4),
                "top_similarity": round(top_score, 4),
                "matches": matches_ui,
                "source_documents": list(dict.fromkeys(used_sources))
            }

        except Exception as e:
            return {
                "found": False,
                "answer": f"Error: {str(e)}",
                "confidence": 0.0,
                "top_similarity": 0.0,
                "matches": [],
                "source_documents": []
            }

    return router