from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserProfile, UserUpdate
from ..schemas.auth import UserInToken
from ..dependencies import get_current_user
from ..models.user import User
from ..modules.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: UserInToken = Depends(get_current_user)):
    logger.info("Profile accessed", extra={"user_id": current_user.id})
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    user_update: UserUpdate,
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Profile update attempt", extra={"user_id": current_user.id})
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    logger.info("Profile updated successfully", extra={"user_id": current_user.id})
    return db_user


@router.delete("/profile")
async def delete_profile(
    current_user: UserInToken = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info("Profile deletion attempt", extra={"user_id": current_user.id})
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    
    logger.info("Profile deleted successfully", extra={"user_id": current_user.id})
    return {"message": "Account deleted successfully"}
