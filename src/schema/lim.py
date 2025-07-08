from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TranscriptRequest(BaseModel):
    transcript: str
    meeting_title: Optional[str] = None
    meeting_date: Optional[str] = None
    participants: Optional[str] = None


class MeetingMinutesResponse(BaseModel):
    meeting_title: Optional[str] = None
    meeting_date: Optional[str] = None
    participants: Optional[str] = None
    summary: str
    key_points: str
    action_items: str
    decisions: str
    original_transcript: str
    generated_at: datetime


class LogEntry(BaseModel):
    id: str
    timestamp: datetime
    request_body: dict
    response_body: dict
    processing_time_ms: float
    status: str


class ErrorResponse(BaseModel):
    detail: str
