from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from modules.minutes_generator import minutes_generator
from modules.logger import api_logger
from schemas.minutes import MinutesRequest, MinutesResponse
from routers.auth import get_current_user
from models.user import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=MinutesResponse)
async def generate_meeting_minutes(
    request: Request,
    minutes_request: MinutesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """会議議事録生成エンドポイント（JWT認証必須）"""
    try:
        if not minutes_request.transcript or not minutes_request.transcript.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="トランスクリプトが空です"
            )
        
        logger.info(f"Generating meeting minutes for user: {current_user.user_id}")
        
        meeting_minutes = await minutes_generator.generate_meeting_minutes(
            transcript=minutes_request.transcript,
            user_id=current_user.user_id
        )
        
        response = MinutesResponse(
            meeting_minutes=meeting_minutes,
            generated_at=datetime.utcnow()
        )
        
        logger.info(f"Meeting minutes generated successfully for user: {current_user.user_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"議事録生成中にエラーが発生しました: {str(e)}"
        api_logger.log_error(
            endpoint="/minutes/generate",
            method="POST",
            error=error_msg,
            user_id=current_user.user_id if current_user else None
        )
        logger.error(f"Error in generate_meeting_minutes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )
