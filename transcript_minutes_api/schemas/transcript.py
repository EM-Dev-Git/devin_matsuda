from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TranscriptRequest(BaseModel):
    transcript: str
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None

class TranscriptResponse(BaseModel):
    meeting_minutes: str
    generated_at: datetime
    status: str = "success"

class GraphTranscriptRequest(BaseModel):
    meeting_id: str
    user_id: Optional[str] = None
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None

class GraphTranscriptInfo(BaseModel):
    id: str
    created_date_time: Optional[str] = None
    meeting_id: str
    transcript_content_url: Optional[str] = None

class GraphTranscriptListResponse(BaseModel):
    transcripts: List[GraphTranscriptInfo]
    meeting_id: str
    status: str = "success"

class GraphTranscriptResponse(BaseModel):
    transcript_content: str
    meeting_id: str
    transcript_id: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: dict
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "GENERATION_FAILED",
                    "message": "Failed to generate meeting minutes",
                    "details": "OpenAI API error or invalid transcript format"
                }
            }
        }
