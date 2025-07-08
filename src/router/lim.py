from fastapi import APIRouter, HTTPException
from typing import List
import time
from datetime import datetime
from schema.lim import (
    TranscriptRequest, MeetingMinutesResponse, LogEntry, ErrorResponse
)
from module.prompt import log_manager
from module.lim import meeting_minutes_generator

router = APIRouter()


@router.post("/generate-minutes", response_model=MeetingMinutesResponse)
async def generate_meeting_minutes(request: TranscriptRequest):
    """Teams会議のトランスクリプトから議事録を生成"""
    start_time = time.time()
    
    try:
        request_body = request.dict()
        
        sections = await meeting_minutes_generator.generate_meeting_minutes(
            transcript=request.original_transcript
        )
        
        response = MeetingMinutesResponse(
            summary=sections["summary"],
            key_points=sections["key_points"],
            action_items=sections["action_items"],
            decisions=sections["decisions"],
            original_transcript=request.original_transcript,
            generated_at=datetime.now()
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        log_manager.create_log_entry(
            request_body=request_body,
            response_body=response.dict(),
            processing_time_ms=processing_time,
            status="success"
        )
        
        return response
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        error_response = {"error": str(e)}
        
        log_manager.create_log_entry(
            request_body=request.dict(),
            response_body=error_response,
            processing_time_ms=processing_time,
            status="error"
        )
        
        raise HTTPException(status_code=500, detail=f"Error generating meeting minutes: {str(e)}")


@router.get("/logs", response_model=List[LogEntry])
async def get_logs():
    """全てのリクエスト/レスポンスログを取得"""
    return log_manager.get_all_logs()


@router.get("/logs/{log_id}", response_model=LogEntry)
async def get_log(log_id: str):
    """特定のログエントリを取得"""
    log_entry = log_manager.get_log(log_id)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return log_entry


@router.delete("/logs")
async def clear_logs():
    """全てのログをクリア"""
    count = log_manager.clear_logs()
    return {"message": f"Cleared {count} log entries"}
