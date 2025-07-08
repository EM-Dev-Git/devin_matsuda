from pydantic import BaseModel
from typing import List, Optional


class PromptModel(BaseModel):
    id: str
    name: str
    content: str
    description: Optional[str] = None


class QuestionRequest(BaseModel):
    question: str
    prompt_id: Optional[str] = None


class QuestionResponse(BaseModel):
    question: str
    answer: str
    prompt_used: Optional[str] = None


class PromptCreateRequest(BaseModel):
    id: str
    name: str
    content: str
    description: Optional[str] = None


class PromptUpdateRequest(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
