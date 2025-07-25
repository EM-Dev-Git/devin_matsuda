from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.auth import UserRegister, Token, UserInToken
from ..modules.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_username,
    get_user_by_email
)
from ..config import settings
from ..dependencies import get_current_user
from ..modules.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    logger.info("User registration attempt", extra={"username": user_data.username, "email": user_data.email})
    
    if get_user_by_username(db, user_data.username):
        logger.warning("Registration failed - username exists", extra={"username": user_data.username})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if get_user_by_email(db, user_data.email):
        logger.warning("Registration failed - email exists", extra={"email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = create_user(db, user_data.username, user_data.email, user_data.password)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info("User registered successfully", extra={"user_id": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info("Login attempt", extra={"username": form_data.username})
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Login failed - invalid credentials", extra={"username": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    logger.info("User logged in successfully", extra={"user_id": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserInToken)
async def read_users_me(current_user: UserInToken = Depends(get_current_user)):
    return current_user
