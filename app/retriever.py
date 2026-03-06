import numpy as np
from app.embedding import embed_query

def retrieve(query, vector_store):
    query_vec = embed_query(query)
    query_vec = np.array(query_vec, dtype="float32")

    return vector_store.search(query_vec)