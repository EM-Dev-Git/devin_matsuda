from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from modules.database import get_db
from modules.auth import authenticate_user, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from modules.logger import logger
from schemas.user import LoginRequest, LoginResponse, ErrorResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse, responses={401: {"model": ErrorResponse}})
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for user: {login_data.user_id}")
        
        user = authenticate_user(db, login_data.user_id, login_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {login_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "AUTHENTICATION_FAILED",
                        "message": "Invalid credentials",
                        "details": "User ID or password is incorrect"
                    }
                }
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.user_id}, expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {login_data.user_id}")
        return LoginResponse(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user {login_data.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error during authentication",
                    "details": str(e)
                }
            }
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid or expired token",
                        "details": "Please login again to get a new token"
                    }
                }
            )
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "TOKEN_ERROR",
                    "message": "Token verification failed",
                    "details": str(e)
                }
            }
        )
