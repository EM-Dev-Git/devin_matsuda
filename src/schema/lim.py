from pydantic import BaseModel
from datetime import datetime


class TranscriptRequest(BaseModel):
    original_transcript: str


class MeetingMinutesResponse(BaseModel):
    meeting_minutes: str
    generated_at: datetime


class ErrorResponse(BaseModel):
    detail: str
