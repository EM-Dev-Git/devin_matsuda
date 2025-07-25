from sqlalchemy.orm import Session
from ..models.transcript import Transcript
from ..schemas.transcript import TranscriptCreate, TranscriptFromGraph
from .openai_client import openai_client
from .graph_client import graph_client
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


async def process_graph_transcript(db: Session, graph_data: TranscriptFromGraph, user_id: int) -> Transcript:
    logger.info("Processing Graph transcript", extra={
        "user_id": user_id, 
        "meeting_id": graph_data.meeting_id,
        "transcript_id": graph_data.transcript_id
    })
    
    transcript_content = await graph_client.get_transcript_content(
        graph_data.meeting_id, 
        graph_data.transcript_id
    )
    
    if not transcript_content:
        raise ValueError("Failed to retrieve transcript content from Microsoft Graph")
    
    db_transcript = Transcript(
        user_id=user_id,
        title=graph_data.title or f"Meeting Transcript - {graph_data.meeting_id}",
        original_transcript=transcript_content,
        status="processing",
        source_type="graph",
        graph_meeting_id=graph_data.meeting_id,
        graph_transcript_id=graph_data.transcript_id,
        graph_organizer_id=graph_data.organizer_id
    )
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    
    try:
        generated_minutes = await openai_client.generate_meeting_minutes(transcript_content)
        
        if generated_minutes:
            db_transcript.generated_minutes = generated_minutes
            db_transcript.status = "completed"
            logger.info("Graph transcript processing completed successfully", extra={"transcript_id": db_transcript.id})
        else:
            db_transcript.status = "failed"
            logger.error("Failed to generate meeting minutes for Graph transcript", extra={"transcript_id": db_transcript.id})
            
    except Exception as e:
        db_transcript.status = "failed"
        logger.error("Error during Graph transcript processing", extra={"transcript_id": db_transcript.id, "error": str(e)})
    
    db.commit()
    db.refresh(db_transcript)
    return db_transcript


async def get_available_graph_transcripts(organizer_id: str, limit: int = 50):
    logger.info("Fetching available Graph transcripts", extra={"organizer_id": organizer_id, "limit": limit})
    
    try:
        transcripts = await graph_client.search_transcripts_by_organizer(organizer_id, limit)
        return transcripts
    except Exception as e:
        logger.error("Failed to fetch available Graph transcripts", extra={"organizer_id": organizer_id, "error": str(e)})
        return []


def delete_transcript(db: Session, transcript_id: int, user_id: int) -> bool:
    transcript = get_transcript_by_id(db, transcript_id, user_id)
    if transcript:
        db.delete(transcript)
        db.commit()
        return True
    return False
