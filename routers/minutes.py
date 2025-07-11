
from fastapi import APIRouter, Depends, HTTPException, status, Request  # FastAPI関連（ルーター、依存性注入、例外、ステータス、リクエスト）をインポート
from sqlalchemy.orm import Session  # データベースセッション型をインポート
from database import get_db  # データベースセッション取得関数をインポート
from modules.minutes_generator import minutes_generator  # 議事録生成クラス（シングルトンインスタンス）をインポート
from modules.logger import api_logger  # API専用ロガー（構造化ログ記録）をインポート
from schemas.minutes import MinutesRequest, MinutesResponse  # 議事録関連のPydanticスキーマをインポート
from routers.auth import get_current_user  # JWT認証依存関数をインポート
from models.user import User  # ユーザーデータベースモデルをインポート
from datetime import datetime  # 日時操作（議事録生成時刻記録用）をインポート
import logging  # 標準ログライブラリをインポート

logger = logging.getLogger(__name__)  # 現在のモジュール名でロガーインスタンスを作成

router = APIRouter()  # FastAPIのAPIRouterインスタンスを作成（議事録関連エンドポイントをグループ化）

@router.post("/generate", response_model=MinutesResponse)  # POSTメソッドで/generateエンドポイントを定義、レスポンスモデルを指定
async def generate_meeting_minutes(  # Teams会議議事録生成を行う非同期関数
    request: Request,  # FastAPIリクエストオブジェクト（メタデータ取得用）
    minutes_request: MinutesRequest,  # 議事録生成リクエスト（transcript含む）
    current_user: User = Depends(get_current_user),  # 認証されたユーザー情報（JWT依存性注入）
    db: Session = Depends(get_db)  # データベースセッション（依存性注入）
):
    """
    Teams会議議事録生成エンドポイント（JWT認証必須）
    
    Teams会議のトランスクリプトを受け取り、OpenAI GPTモデルを使用して
    構造化された議事録を生成します。このエンドポイントはJWT認証が必須で、
    認証されたユーザーのみがアクセス可能です。
    
    処理フロー：
    1. JWT認証の確認（get_current_user依存関数により自動実行）
    2. トランスクリプトの入力検証
    3. 議事録生成処理の実行
    4. レスポンスデータの構築
    5. 成功ログの記録
    6. 議事録データの返却
    
    引数:
        request (Request): FastAPIリクエストオブジェクト（メタデータ取得用）
        minutes_request (MinutesRequest): 議事録生成リクエスト（transcript含む）
        current_user (User): 認証されたユーザー情報（JWT依存性注入）
        db (Session): データベースセッション（依存性注入）
        
    戻り値:
        MinutesResponse: 生成された議事録と生成時刻
        
    例外:
        HTTPException: トランスクリプトが空の場合（400 Bad Request）
        HTTPException: JWT認証失敗時（401 Unauthorized）
        HTTPException: 内部サーバーエラー時（500 Internal Server Error）
        
    認証要件:
        - 有効なJWTトークンがAuthorizationヘッダーに必要
        - トークンは事前に/auth/loginエンドポイントで取得
        
    使用例:
        POST /minutes/generate
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        {
            "transcript": "山田: おはようございます。今日の会議を始めます..."
        }
        
        レスポンス:
        {
            "meeting_minutes": "## 会議概要\n参加者: 山田、田中...",
            "generated_at": "2025-01-11T00:05:30.123456"
        }
    """
    try:
        if not minutes_request.transcript or not minutes_request.transcript.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="トランスクリプトが空です"
            )
        
        logger.info(f"Generating meeting minutes for user: {current_user.user_id}")
        
        meeting_minutes = await minutes_generator.generate_meeting_minutes(
            transcript=minutes_request.transcript,  # Teams会議のトランスクリプト
            user_id=current_user.user_id           # 認証されたユーザーID（ログ記録用）
        )
        
        response = MinutesResponse(
            meeting_minutes=meeting_minutes,  # OpenAI APIで生成された議事録（Markdown形式）
            generated_at=datetime.utcnow()   # 議事録生成完了時刻（UTC）
        )
        
        logger.info(f"Meeting minutes generated successfully for user: {current_user.user_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        
        error_msg = f"議事録生成中にエラーが発生しました: {str(e)}"
        
        api_logger.log_error(
            endpoint="/minutes/generate",                              # エラー発生エンドポイント
            method="POST",                                             # HTTPメソッド
            error=error_msg,                                          # エラーメッセージ
            user_id=current_user.user_id if current_user else None    # エラー発生ユーザーID（認証済みの場合）
        )
        
        logger.error(f"Error in generate_meeting_minutes: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました"
        )
