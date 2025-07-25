from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.transcript import TranscriptCreate, TranscriptResponse, TranscriptList, TranscriptUpdate
from ..schemas.auth import UserInToken
from ..dependencies import get_current_user
from ..modules.transcript_processor import (
    process_transcript,
    get_user_transcripts,
    get_transcript_by_id,
    update_transcript,
    delete_transcript
)
from ..modules.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("/", response_model=TranscriptResponse)
async def create_transcript(
    transcript_data: TranscriptCreate,
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Transcript creation request", extra={"user_id": current_user.id, "title": transcript_data.title})
    transcript = await process_transcript(db, transcript_data, current_user.id)
    return transcript


@router.get("/", response_model=List[TranscriptList])
async def get_transcripts(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Transcripts list request", extra={"user_id": current_user.id, "skip": skip, "limit": limit})
    transcripts = get_user_transcripts(db, current_user.id, skip, limit)
    return transcripts


@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(
    transcript_id: int,
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Transcript detail request", extra={"user_id": current_user.id, "transcript_id": transcript_id})
    transcript = get_transcript_by_id(db, transcript_id, current_user.id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript


@router.put("/{transcript_id}", response_model=TranscriptResponse)
async def update_transcript_endpoint(
    transcript_id: int,
    transcript_update: TranscriptUpdate,
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Transcript update request", extra={"user_id": current_user.id, "transcript_id": transcript_id})
    update_data = transcript_update.dict(exclude_unset=True)
    transcript = update_transcript(db, transcript_id, current_user.id, update_data)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript


@router.delete("/{transcript_id}")
async def delete_transcript_endpoint(
    transcript_id: int,
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Transcript deletion request", extra={"user_id": current_user.id, "transcript_id": transcript_id})
    success = delete_transcript(db, transcript_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {"message": "Transcript deleted successfully"}
