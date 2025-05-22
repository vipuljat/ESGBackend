from pydantic import BaseModel
from typing import Any, List

class ESGQuestion(BaseModel):
    question_id: str  # e.g., "A0/1", "C1_1"
    response: Any  # Flexible to handle text, tables, nested objects

class ESGQuestionUpdate(BaseModel):
    response: Any