from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TranscriptBase(BaseModel):
    title: Optional[str] = None
    original_transcript: str


class TranscriptCreate(TranscriptBase):
    pass


class TranscriptUpdate(BaseModel):
    title: Optional[str] = None
    original_transcript: Optional[str] = None


class TranscriptResponse(TranscriptBase):
    id: int
    user_id: int
    generated_minutes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TranscriptList(BaseModel):
    id: int
    title: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
