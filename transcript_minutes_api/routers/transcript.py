from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from modules.database import get_db, User, MeetingMinutes
from modules.auth import get_current_user
from modules.openai_client import generate_meeting_minutes
from modules.logger import logger, log_request, log_error, log_openai_request
from schemas.transcript import TranscriptRequest, TranscriptResponse, ErrorResponse

router = APIRouter(prefix="/transcript", tags=["transcript"])

@router.post("/generate", response_model=TranscriptResponse, responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_minutes(
    request: TranscriptRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log_request(current_user, "/transcript/generate", "POST")
    
    try:
        if not request.transcript.strip():
            logger.warning(f"Empty transcript provided by user: {current_user}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "Transcript cannot be empty",
                        "details": "Please provide a valid transcript text"
                    }
                }
            )
        
        log_openai_request(current_user, len(request.transcript))
        
        meeting_minutes = generate_meeting_minutes(
            transcript=request.transcript,
            meeting_title=request.meeting_title,
            participants=request.participants
        )
        
        user = db.query(User).filter(User.username == current_user).first()
        if user:
            participants_str = ", ".join(request.participants) if request.participants else None
            meeting_record = MeetingMinutes(
                user_id=user.id,
                original_transcript=request.transcript,
                generated_minutes=meeting_minutes,
                meeting_title=request.meeting_title,
                participants=participants_str
            )
            db.add(meeting_record)
            db.commit()
            logger.info(f"Meeting minutes saved to database for user: {current_user}")
        
        response = TranscriptResponse(
            meeting_minutes=meeting_minutes,
            generated_at=datetime.utcnow(),
            status="success"
        )
        
        logger.info(f"Successfully generated meeting minutes for user: {current_user}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(current_user, "Meeting minutes generation failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "GENERATION_FAILED",
                    "message": "Failed to generate meeting minutes",
                    "details": str(e)
                }
            }
        )
