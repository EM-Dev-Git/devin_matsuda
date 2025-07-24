from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranscriptRequest(BaseModel):
    transcript: str
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None

class TranscriptResponse(BaseModel):
    meeting_minutes: str
    generated_at: datetime
    status: str

class ErrorResponse(BaseModel):
    error: dict

class MeetingMinutesHistory(BaseModel):
    id: int
    meeting_title: Optional[str]
    participants: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
