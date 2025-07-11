
from fastapi import APIRouter, Depends, HTTPException, status, Request  # FastAPI関連（ルーター、依存性注入、例外、ステータス、リクエスト）
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # JWT認証用セキュリティスキーム
from sqlalchemy.orm import Session  # データベースセッション型
from database import get_db  # データベースセッション取得関数
from modules.auth_manager import AuthManager  # 認証管理クラス（JWT・パスワード処理）
from modules.logger import api_logger  # API専用ロガー（構造化ログ記録）
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse  # 認証関連のPydanticスキーマ
from schemas.user import UserCreate  # ユーザー作成用Pydanticスキーマ
import logging  # 標準ログライブラリ

logger = logging.getLogger(__name__)

router = APIRouter()

security = HTTPBearer()

@router.post("/login", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    ユーザーログインエンドポイント
    
    ユーザーIDとパスワードを受け取り、認証に成功した場合はJWTアクセストークンを返します。
    認証試行はログに記録され、セキュリティ監視に活用されます。
    
    処理フロー：
    1. クライアントIPアドレスの取得
    2. リクエストログの記録
    3. ユーザー認証の実行
    4. 認証失敗時のエラーハンドリング
    5. JWTトークンの生成
    6. 認証成功ログの記録
    7. レスポンスログの記録
    8. JWTトークンの返却
    
    引数:
        request (Request): FastAPIリクエストオブジェクト（IPアドレス取得用）
        login_data (LoginRequest): ログイン情報（user_id, password）
        db (Session): データベースセッション（依存性注入）
        
    戻り値:
        LoginResponse: JWTアクセストークンとトークンタイプ
        
    例外:
        HTTPException: 認証失敗時（401 Unauthorized）
        HTTPException: 内部サーバーエラー時（500 Internal Server Error）
        
    使用例:
        POST /auth/login
        {
            "user_id": "yamada_taro",
            "password": "secure_password123"
        }
        
        レスポンス:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        api_logger.log_request(
            endpoint="/auth/login",                    # エンドポイント名
            method="POST",                             # HTTPメソッド
            user_id=login_data.user_id,               # ログイン試行ユーザーID
            request_body={"user_id": login_data.user_id}  # リクエストボディ（パスワード除外）
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
            endpoint="/auth/login",                    # エンドポイント名
            method="POST",                             # HTTPメソッド
            status_code=200,                           # HTTPステータスコード（成功）
            user_id=login_data.user_id,               # ログインユーザーID
            response_body={"token_generated": True}    # レスポンス概要（トークン値は除外）
        )
        
        logger.info(f"User {login_data.user_id} logged in successfully")
        
        return LoginResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        
        error_msg = f"ログイン処理中にエラーが発生しました: {str(e)}"
        
        api_logger.log_error(
            endpoint="/auth/login",      # エラー発生エンドポイント
            method="POST",               # HTTPメソッド
            error=error_msg,            # エラーメッセージ
            user_id=login_data.user_id  # エラー発生ユーザーID
        )
        
        logger.error(f"Login error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )

@router.post("/register", response_model=RegisterResponse)
async def register(request: Request, register_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    ユーザー登録エンドポイント
    
    新規ユーザーアカウントを作成します。ユーザーIDの重複チェックを行い、
    パスワードは安全にハッシュ化してデータベースに保存されます。
    
    処理フロー：
    1. クライアントIPアドレスの取得
    2. リクエストログの記録
    3. ユーザーID重複チェック
    4. 重複時のエラーハンドリング
    5. 新規ユーザーの作成（パスワードハッシュ化含む）
    6. レスポンスログの記録
    7. 登録完了メッセージの返却
    
    引数:
        request (Request): FastAPIリクエストオブジェクト（IPアドレス取得用）
        register_data (RegisterRequest): 登録情報（user_id, password）
        db (Session): データベースセッション（依存性注入）
        
    戻り値:
        RegisterResponse: 登録完了メッセージとユーザーID
        
    例外:
        HTTPException: ユーザーID重複時（400 Bad Request）
        HTTPException: 内部サーバーエラー時（500 Internal Server Error）
        
    使用例:
        POST /auth/register
        {
            "user_id": "yamada_taro",
            "password": "secure_password123"
        }
        
        レスポンス:
        {
            "message": "ユーザー登録が完了しました",
            "user_id": "yamada_taro"
        }
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        api_logger.log_request(
            endpoint="/auth/register",                 # エンドポイント名
            method="POST",                             # HTTPメソッド
            user_id=register_data.user_id,            # 登録予定ユーザーID
            request_body={"user_id": register_data.user_id}  # リクエストボディ（パスワード除外）
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
            endpoint="/auth/register",                 # エンドポイント名
            method="POST",                             # HTTPメソッド
            status_code=201,                           # HTTPステータスコード（作成成功）
            user_id=register_data.user_id,            # 登録されたユーザーID
            response_body={"user_created": True}       # レスポンス概要
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
            endpoint="/auth/register",        # エラー発生エンドポイント
            method="POST",                    # HTTPメソッド
            error=error_msg,                 # エラーメッセージ
            user_id=register_data.user_id    # エラー発生ユーザーID
        )
        
        logger.error(f"Registration error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    JWTトークンから現在のユーザーを取得する依存性注入関数
    
    保護されたエンドポイントで使用される認証依存関数です。
    クライアントから送信されたJWTトークンを検証し、有効な場合は
    対応するユーザーオブジェクトを返します。
    
    処理フロー：
    1. Authorizationヘッダーからトークン抽出
    2. JWTトークンの検証（署名・有効期限チェック）
    3. トークンからユーザーID抽出
    4. データベースからユーザー情報取得
    5. ユーザー存在確認
    6. ユーザーオブジェクト返却
    
    引数:
        credentials (HTTPAuthorizationCredentials): JWT認証情報（依存性注入）
        db (Session): データベースセッション（依存性注入）
        
    戻り値:
        User: 認証されたユーザーのデータベースオブジェクト
        
    例外:
        HTTPException: トークンが無効な場合（401 Unauthorized）
        HTTPException: ユーザーが見つからない場合（401 Unauthorized）
        HTTPException: 認証処理でエラーが発生した場合（401 Unauthorized）
        
    使用例:
        @router.get("/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello, {current_user.user_id}!"}
        
        クライアント側:
        GET /protected
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    try:
        token = credentials.credentials
        
        user_id = AuthManager.verify_token(token)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです",
                headers={"WWW-Authenticate": "Bearer"},  # RFC 6750準拠のWWW-Authenticateヘッダー
            )
        
        user = AuthManager.get_user_by_user_id(db, user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません",
                headers={"WWW-Authenticate": "Bearer"},  # RFC 6750準拠のWWW-Authenticateヘッダー
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        
        logger.error(f"Token verification error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました",
            headers={"WWW-Authenticate": "Bearer"},  # RFC 6750準拠のWWW-Authenticateヘッダー
        )
