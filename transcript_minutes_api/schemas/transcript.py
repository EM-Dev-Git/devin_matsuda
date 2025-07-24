<<<<<<< HEAD
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TranscriptRequest(BaseModel):
    transcript: str
    meeting_title: Optional[str] = ""
    participants: Optional[List[str]] = []

class GraphTranscriptRequest(BaseModel):
    user_id: str
    meeting_id: str
    transcript_id: str
    meeting_title: Optional[str] = ""

class MeetingInfo(BaseModel):
    id: str
    subject: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    join_url: Optional[str]
    organizer: Optional[str]

class TranscriptInfo(BaseModel):
    id: str
    meeting_id: str
    created_date_time: Optional[str]
    content_url: Optional[str]

class MinutesResponse(BaseModel):
    meeting_minutes: str
    generated_at: datetime
    status: str
    meeting_title: Optional[str] = None
    source: str = "manual"

class MeetingMinutesHistory(BaseModel):
    id: int
    meeting_title: Optional[str]
    participants: Optional[str]
    meeting_id: Optional[str]
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True
||||||| ab1cd5e
=======
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
>>>>>>> af772fe42f0bc45e327e1468df85f437de342f3b
