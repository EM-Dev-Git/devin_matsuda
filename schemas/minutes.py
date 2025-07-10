from pydantic import BaseModel
from datetime import datetime

class MinutesRequest(BaseModel):
    transcript: str

class MinutesResponse(BaseModel):
    meeting_minutes: str
    generated_at: datetime
