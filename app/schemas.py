from pydantic import BaseModel
from typing import List

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    confidence: str
    source_documents: List[str]
    similarity_score: float
