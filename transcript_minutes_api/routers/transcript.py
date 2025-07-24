from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from modules.openai_client import generate_meeting_minutes
from modules.graph_client import list_meeting_transcripts, get_transcript_content, get_meeting_transcript_for_minutes
from modules.logger import logger
from schemas.transcript import (
    TranscriptRequest, TranscriptResponse, ErrorResponse,
    GraphTranscriptRequest, GraphTranscriptListResponse, GraphTranscriptResponse, GraphTranscriptInfo
)
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

@router.get("/list/{meeting_id}", response_model=GraphTranscriptListResponse, responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def list_transcripts(
    meeting_id: str,
    user_id: str = None,
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"List transcripts request for meeting {meeting_id} from user: {current_user}")
        
        if not meeting_id or not meeting_id.strip():
            logger.warning(f"Empty meeting ID provided by user: {current_user}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "Meeting ID cannot be empty",
                        "details": "Please provide a valid meeting ID"
                    }
                }
            )
        
        transcripts_data = await list_meeting_transcripts(meeting_id, user_id)
        
        transcripts = [
            GraphTranscriptInfo(
                id=t["id"],
                created_date_time=t["created_date_time"],
                meeting_id=t["meeting_id"],
                transcript_content_url=t["transcript_content_url"]
            )
            for t in transcripts_data
        ]
        
        logger.info(f"Listed {len(transcripts)} transcripts for meeting {meeting_id} for user: {current_user}")
        return GraphTranscriptListResponse(
            transcripts=transcripts,
            meeting_id=meeting_id,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing transcripts for meeting {meeting_id} for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "GRAPH_API_ERROR",
                    "message": "Failed to list meeting transcripts",
                    "details": str(e)
                }
            }
        )

@router.get("/fetch/{meeting_id}/{transcript_id}", response_model=GraphTranscriptResponse, responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def fetch_transcript(
    meeting_id: str,
    transcript_id: str,
    user_id: str = None,
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"Fetch transcript request for meeting {meeting_id}, transcript {transcript_id} from user: {current_user}")
        
        if not meeting_id or not meeting_id.strip():
            logger.warning(f"Empty meeting ID provided by user: {current_user}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "Meeting ID cannot be empty",
                        "details": "Please provide a valid meeting ID"
                    }
                }
            )
        
        if not transcript_id or not transcript_id.strip():
            logger.warning(f"Empty transcript ID provided by user: {current_user}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "Transcript ID cannot be empty",
                        "details": "Please provide a valid transcript ID"
                    }
                }
            )
        
        transcript_content = await get_transcript_content(meeting_id, transcript_id, user_id)
        
        logger.info(f"Fetched transcript content for meeting {meeting_id}, transcript {transcript_id} for user: {current_user}")
        return GraphTranscriptResponse(
            transcript_content=transcript_content,
            meeting_id=meeting_id,
            transcript_id=transcript_id,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transcript for meeting {meeting_id}, transcript {transcript_id} for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "GRAPH_API_ERROR",
                    "message": "Failed to fetch transcript content",
                    "details": str(e)
                }
            }
        )

@router.post("/generate-from-graph", response_model=TranscriptResponse, responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_minutes_from_graph(
    request: GraphTranscriptRequest,
    current_user: str = Depends(get_current_user)
):
    try:
        logger.info(f"Generate minutes from Graph request for meeting {request.meeting_id} from user: {current_user}")
        
        if not request.meeting_id or not request.meeting_id.strip():
            logger.warning(f"Empty meeting ID provided by user: {current_user}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": "Meeting ID cannot be empty",
                        "details": "Please provide a valid meeting ID"
                    }
                }
            )
        
        transcript_content = await get_meeting_transcript_for_minutes(request.meeting_id, request.user_id)
        
        meeting_minutes = await generate_meeting_minutes(
            transcript=transcript_content,
            meeting_title=request.meeting_title,
            participants=request.participants
        )
        
        logger.info(f"Meeting minutes generated from Graph transcript successfully for user: {current_user}")
        return TranscriptResponse(
            meeting_minutes=meeting_minutes,
            generated_at=datetime.utcnow(),
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating meeting minutes from Graph for meeting {request.meeting_id} for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "GRAPH_GENERATION_FAILED",
                    "message": "Failed to generate meeting minutes from Graph transcript",
                    "details": str(e)
                }
            }
        )
