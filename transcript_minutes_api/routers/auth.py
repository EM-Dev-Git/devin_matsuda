from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from modules.database import get_db, User
from modules.auth import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from modules.logger import logger, log_auth_attempt
from schemas.user import UserCreate, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=dict)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"User registration attempt: {user.username}")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logger.warning(f"Registration failed - username already exists: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        logger.warning(f"Registration failed - email already exists: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User registered successfully: {user.username}")
    return {"message": "User registered successfully", "username": user.username}

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt: {user_credentials.username}")
    
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        log_auth_attempt(user_credentials.username, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        log_auth_attempt(user_credentials.username, False)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    log_auth_attempt(user_credentials.username, True)
    logger.info(f"Login successful: {user_credentials.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
