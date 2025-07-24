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
