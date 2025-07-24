from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from modules.openai_client import generate_meeting_minutes
from modules.logger import logger
from schemas.transcript import TranscriptRequest, TranscriptResponse, ErrorResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/transcript", tags=["transcript"])

@router.post("/generate", response_model=TranscriptResponse, responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_minutes(
    request: TranscriptRequest,
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"Meeting minutes generation request from user: {current_user}")
        logger.info(f"Transcript length: {len(request.transcript)} characters")
        
        if not request.transcript.strip():
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
        
        meeting_minutes = await generate_meeting_minutes(
            transcript=request.transcript,
            meeting_title=request.meeting_title,
            participants=request.participants
        )
        
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
        logger.error(f"Meeting minutes generation error for user {current_user}: {str(e)}")
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
