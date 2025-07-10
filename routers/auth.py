from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from modules.auth_manager import AuthManager
from modules.logger import api_logger
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from schemas.user import UserCreate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        api_logger.log_request(
            endpoint="/auth/login",
            method="POST",
            user_id=login_data.user_id,
            request_body={"user_id": login_data.user_id}
        )
        
        user = AuthManager.authenticate_user(db, login_data.user_id, login_data.password)
        if not user:
            api_logger.log_auth_attempt(login_data.user_id, False, client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーIDまたはパスワードが正しくありません"
            )
        
        access_token = AuthManager.create_access_token(data={"sub": user.user_id})
        
        api_logger.log_auth_attempt(login_data.user_id, True, client_ip)
        api_logger.log_response(
            endpoint="/auth/login",
            method="POST",
            status_code=200,
            user_id=login_data.user_id,
            response_body={"token_generated": True}
        )
        
        logger.info(f"User {login_data.user_id} logged in successfully")
        
        return LoginResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"ログイン処理中にエラーが発生しました: {str(e)}"
        api_logger.log_error(
            endpoint="/auth/login",
            method="POST",
            error=error_msg,
            user_id=login_data.user_id
        )
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )

@router.post("/register", response_model=RegisterResponse)
async def register(request: Request, register_data: RegisterRequest, db: Session = Depends(get_db)):
    """ユーザー登録"""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        api_logger.log_request(
            endpoint="/auth/register",
            method="POST",
            user_id=register_data.user_id,
            request_body={"user_id": register_data.user_id}
        )
        
        existing_user = AuthManager.get_user_by_user_id(db, register_data.user_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このユーザーIDは既に使用されています"
            )
        
        user_create = UserCreate(user_id=register_data.user_id, password=register_data.password)
        user = AuthManager.create_user(db, user_create)
        
        api_logger.log_response(
            endpoint="/auth/register",
            method="POST",
            status_code=201,
            user_id=register_data.user_id,
            response_body={"user_created": True}
        )
        
        logger.info(f"User {register_data.user_id} registered successfully")
        
        return RegisterResponse(
            message="ユーザー登録が完了しました",
            user_id=user.user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"ユーザー登録中にエラーが発生しました: {str(e)}"
        api_logger.log_error(
            endpoint="/auth/register",
            method="POST",
            error=error_msg,
            user_id=register_data.user_id
        )
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """JWT トークンから現在のユーザーを取得"""
    try:
        token = credentials.credentials
        user_id = AuthManager.verify_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = AuthManager.get_user_by_user_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました",
            headers={"WWW-Authenticate": "Bearer"},
        )
