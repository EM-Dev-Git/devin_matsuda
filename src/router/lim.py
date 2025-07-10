from fastapi import APIRouter, HTTPException
import time
from datetime import datetime
from schema.lim import TranscriptRequest, MeetingMinutesResponse, ErrorResponse
from module.lim import meeting_minutes_generator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-minutes", response_model=MeetingMinutesResponse)
async def generate_meeting_minutes(request: TranscriptRequest):
    """Teams会議のトランスクリプトから議事録を生成"""
    start_time = time.time()
    
    logger.info(f"Meeting minutes generation request received")
    logger.debug(f"Request body: {request.dict()}")
    
    try:
        meeting_minutes_text = await meeting_minutes_generator.generate_meeting_minutes(
            transcript=request.original_transcript
        )
        
        response = MeetingMinutesResponse(
            meeting_minutes=meeting_minutes_text,
            generated_at=datetime.now()
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Meeting minutes generated successfully in {processing_time:.2f}ms")
        logger.debug(f"Response body: {response.dict()}")
        
        print(f"Meeting minutes generated in {processing_time:.2f}ms")
        
        return response
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        error_msg = f"Error generating meeting minutes: {str(e)}"
        
        logger.error(f"{error_msg} (took {processing_time:.2f}ms)")
        print(f"{error_msg} (took {processing_time:.2f}ms)")
        
        raise HTTPException(status_code=500, detail=error_msg)
