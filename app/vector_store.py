from typing import List, Dict, Any
import numpy as np


class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.embeddings = None  # shape: (N, D)
        self.texts: List[str] = []
        self.sources: List[str] = []

    def add(self, embeddings: List[List[float]], texts: List[str], sources: List[str]):
        emb = np.array(embeddings, dtype=np.float32)

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10
        emb = emb / norms

        self.embeddings = emb
        self.texts = list(texts)
        self.sources = list(sources)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self.embeddings is None or len(self.texts) == 0:
            return []

        q = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-10)

        # cosine similarity (because both normalized): dot product
        sims = (self.embeddings @ q.T).reshape(-1)  # shape: (N,)

        # top_k indices
        top_k = min(top_k, len(sims))
        idxs = np.argpartition(-sims, top_k - 1)[:top_k]
        idxs = idxs[np.argsort(-sims[idxs])]

        results = []
        for i in idxs:
            results.append({
                "score": float(sims[i]),  # cosine similarity in [-1,1], usually [0,1]
                "text": self.texts[i],
                "source": self.sources[i]
            })
        return results