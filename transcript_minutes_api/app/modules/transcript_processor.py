from sqlalchemy.orm import Session
from ..models.transcript import Transcript
from ..schemas.transcript import TranscriptCreate
from .openai_client import openai_client
from .logger import get_logger

logger = get_logger(__name__)


async def process_transcript(db: Session, transcript_data: TranscriptCreate, user_id: int) -> Transcript:
    logger.info("Processing new transcript", extra={"user_id": user_id, "title": transcript_data.title})
    
    db_transcript = Transcript(
        user_id=user_id,
        title=transcript_data.title,
        original_transcript=transcript_data.original_transcript,
        status="processing"
    )
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    
    try:
        generated_minutes = await openai_client.generate_meeting_minutes(transcript_data.original_transcript)
        
        if generated_minutes:
            db_transcript.generated_minutes = generated_minutes
            db_transcript.status = "completed"
            logger.info("Transcript processing completed successfully", extra={"transcript_id": db_transcript.id})
        else:
            db_transcript.status = "failed"
            logger.error("Failed to generate meeting minutes", extra={"transcript_id": db_transcript.id})
            
    except Exception as e:
        db_transcript.status = "failed"
        logger.error("Error during transcript processing", extra={"transcript_id": db_transcript.id, "error": str(e)})
    
    db.commit()
    db.refresh(db_transcript)
    return db_transcript


def get_user_transcripts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transcript).filter(Transcript.user_id == user_id).offset(skip).limit(limit).all()


def get_transcript_by_id(db: Session, transcript_id: int, user_id: int) -> Transcript:
    return db.query(Transcript).filter(
        Transcript.id == transcript_id,
        Transcript.user_id == user_id
    ).first()


def update_transcript(db: Session, transcript_id: int, user_id: int, update_data: dict) -> Transcript:
    transcript = get_transcript_by_id(db, transcript_id, user_id)
    if transcript:
        for key, value in update_data.items():
            if hasattr(transcript, key) and value is not None:
                setattr(transcript, key, value)
        db.commit()
        db.refresh(transcript)
    return transcript


def delete_transcript(db: Session, transcript_id: int, user_id: int) -> bool:
    transcript = get_transcript_by_id(db, transcript_id, user_id)
    if transcript:
        db.delete(transcript)
        db.commit()
        return True
    return False
