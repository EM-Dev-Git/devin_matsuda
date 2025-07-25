from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TranscriptBase(BaseModel):
    title: Optional[str] = None
    original_transcript: str


class TranscriptCreate(TranscriptBase):
    pass


class TranscriptFromGraph(BaseModel):
    meeting_id: str
    transcript_id: str
    organizer_id: Optional[str] = None
    title: Optional[str] = None


class TranscriptUpdate(BaseModel):
    title: Optional[str] = None
    original_transcript: Optional[str] = None


class TranscriptResponse(TranscriptBase):
    id: int
    user_id: int
    generated_minutes: Optional[str] = None
    status: str
    source_type: str
    graph_meeting_id: Optional[str] = None
    graph_transcript_id: Optional[str] = None
    graph_organizer_id: Optional[str] = None
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
