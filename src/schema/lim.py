from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TranscriptRequest(BaseModel):
    original_transcript: str


class MeetingMinutesResponse(BaseModel):
    meeting_minutes: str
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
