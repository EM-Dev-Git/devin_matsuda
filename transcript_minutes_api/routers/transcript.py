from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from modules.database import get_db, User, MeetingMinutes
from modules.auth import get_current_user
from modules.openai_client import openai_client
from modules.graph_client import graph_client
from schemas.transcript import (
    TranscriptRequest, 
    GraphTranscriptRequest,
    MinutesResponse, 
    MeetingInfo, 
    TranscriptInfo,
    MeetingMinutesHistory
)
from modules.logger import logger, log_request, log_error, log_openai_request

router = APIRouter(prefix="/transcript", tags=["transcript"])

@router.post("/generate", response_model=MinutesResponse)
async def generate_minutes(
    request: TranscriptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log_request(current_user.username, "/transcript/generate", "POST")
    
    try:
        if not request.transcript.strip():
            logger.warning(f"Empty transcript provided by user: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript cannot be empty"
            )
        
        logger.info(f"Generating minutes for user: {current_user.username}")
        log_openai_request(current_user.username, len(request.transcript))
        
        minutes = await openai_client.generate_minutes(
            transcript=request.transcript,
            meeting_title=request.meeting_title,
            participants=request.participants
        )
        
        db_minutes = MeetingMinutes(
            user_id=current_user.id,
            original_transcript=request.transcript,
            generated_minutes=minutes,
            meeting_title=request.meeting_title,
            participants=", ".join(request.participants) if request.participants else None,
            source="manual"
        )
        
        db.add(db_minutes)
        db.commit()
        
        logger.info(f"Minutes generated and saved for user: {current_user.username}")
        
        return MinutesResponse(
            meeting_minutes=minutes,
            generated_at=datetime.utcnow(),
            status="success",
            meeting_title=request.meeting_title,
            source="manual"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(current_user.username, "Meeting minutes generation failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"議事録生成に失敗しました: {str(e)}"
        )

@router.get("/meetings", response_model=List[MeetingInfo])
async def get_user_meetings(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    log_request(current_user.username, "/transcript/meetings", "GET")
    
    try:
        logger.info(f"Fetching meetings for Graph user: {user_id}")
        
        meetings = await graph_client.get_user_meetings(user_id)
        
        return [MeetingInfo(**meeting) for meeting in meetings]
        
    except Exception as e:
        log_error(current_user.username, "Error fetching meetings", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ミーティング取得に失敗しました: {str(e)}"
        )

@router.get("/meetings/{meeting_id}/transcripts", response_model=List[TranscriptInfo])
async def get_meeting_transcripts(
    meeting_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    log_request(current_user.username, f"/transcript/meetings/{meeting_id}/transcripts", "GET")
    
    try:
        logger.info(f"Fetching transcripts for meeting: {meeting_id}")
        
        transcripts = await graph_client.get_meeting_transcripts(user_id, meeting_id)
        
        return [TranscriptInfo(**transcript) for transcript in transcripts]
        
    except Exception as e:
        log_error(current_user.username, "Error fetching transcripts", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"トランスクリプト取得に失敗しました: {str(e)}"
        )

@router.post("/generate-from-graph", response_model=MinutesResponse)
async def generate_minutes_from_graph(
    request: GraphTranscriptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log_request(current_user.username, "/transcript/generate-from-graph", "POST")
    
    try:
        logger.info(f"Generating minutes from Graph transcript: {request.transcript_id}")
        
        transcript_content = await graph_client.get_transcript_content(
            request.user_id, 
            request.meeting_id, 
            request.transcript_id
        )
        
        log_openai_request(current_user.username, len(transcript_content))
        
        minutes = await openai_client.generate_minutes(
            transcript=transcript_content,
            meeting_title=request.meeting_title,
            participants=[]
        )
        
        db_minutes = MeetingMinutes(
            user_id=current_user.id,
            original_transcript=transcript_content,
            generated_minutes=minutes,
            meeting_title=request.meeting_title,
            meeting_id=request.meeting_id,
            source="graph"
        )
        
        db.add(db_minutes)
        db.commit()
        
        logger.info(f"Minutes generated from Graph transcript for user: {current_user.username}")
        
        return MinutesResponse(
            meeting_minutes=minutes,
            generated_at=datetime.utcnow(),
            status="success",
            meeting_title=request.meeting_title,
            source="graph"
        )
        
    except Exception as e:
        log_error(current_user.username, "Error generating minutes from Graph", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph APIからの議事録生成に失敗しました: {str(e)}"
        )

@router.get("/history", response_model=List[MeetingMinutesHistory])
async def get_minutes_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log_request(current_user.username, "/transcript/history", "GET")
    
    try:
        logger.info(f"Fetching minutes history for user: {current_user.username}")
        
        history = db.query(MeetingMinutes).filter(
            MeetingMinutes.user_id == current_user.id
        ).order_by(MeetingMinutes.created_at.desc()).all()
        
        return history
        
    except Exception as e:
        log_error(current_user.username, "Error fetching history", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"履歴取得に失敗しました: {str(e)}"
        )
