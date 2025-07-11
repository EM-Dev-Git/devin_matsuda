
from fastapi import FastAPI  # FastAPIフレームワークのメインクラス
from fastapi.middleware.cors import CORSMiddleware  # CORS（Cross-Origin Resource Sharing）対応のミドルウェア
from routers import auth, minutes  # 認証と議事録生成のルーターをインポート
from database import create_tables  # データベーステーブル作成関数をインポート
from modules.logger import api_logger  # カスタムAPIロガーをインポート
import uvicorn  # ASGIサーバー（FastAPIアプリケーションを実行するためのサーバー）
import logging  # Pythonの標準ログライブラリ
import os  # 環境変数を取得するためのOSライブラリ
from dotenv import load_dotenv  # .envファイルから環境変数を読み込むライブラリ

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # INFOレベル以上のログを出力
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # ログの出力形式：時刻 - ロガー名 - レベル - メッセージ
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Teams会議議事録生成API",  # API文書に表示されるタイトル
    description="Teams会議のトランスクリプトからOpenAIを使用して議事録を自動生成するAPI。JWT認証とログ機能を含む。",  # API文書に表示される説明
    version="1.0.0",  # APIのバージョン
    docs_url="/docs",  # Swagger UIのURL（自動生成されるAPI文書）
    redoc_url="/redoc"  # ReDocのURL（別形式のAPI文書）
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンからのリクエストを許可（本番環境では特定のドメインに制限することを推奨）
    allow_credentials=True,  # 認証情報（Cookie、Authorization headerなど）を含むリクエストを許可
    allow_methods=["*"],  # すべてのHTTPメソッド（GET、POST、PUT、DELETEなど）を許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(minutes.router, prefix="/minutes", tags=["Meeting Minutes"])

@app.on_event("startup")
async def startup_event():
    """
    アプリケーション起動時に実行される処理
    データベーステーブルの作成・確認を行い、システムの初期化を完了します
    """
    logger.info("Starting Teams Meeting Minutes API...")  # 起動開始ログ
    create_tables()  # データベーステーブルの作成または存在確認
    logger.info("Database tables created/verified")  # データベース初期化完了ログ
    logger.info("Teams Meeting Minutes API started successfully")  # 起動完了ログ

@app.get("/")
async def root():
    """
    ルートエンドポイント（GET /）
    APIの基本情報と利用可能なエンドポイントの一覧を返します
    システムの動作確認やAPI探索の起点として使用されます
    """
    return {
        "message": "Teams会議議事録生成API",  # APIの名前
        "version": "1.0.0",  # APIのバージョン情報
        "endpoints": {  # 利用可能なエンドポイントの説明
            "auth": "/auth (login, register)",  # 認証関連エンドポイント
            "minutes": "/minutes (generate - JWT required)",  # 議事録生成エンドポイント（JWT認証必須）
            "docs": "/docs"  # API文書のURL
        }
    }

@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント（GET /health）
    システムの稼働状況を確認するためのエンドポイント
    ロードバランサーや監視システムから定期的に呼び出されることを想定
    """
    return {"status": "healthy", "service": "Teams Meeting Minutes API"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")  # サーバーのホストアドレス（デフォルト：すべてのインターフェースでリッスン）
    port = int(os.getenv("PORT", "8000"))  # サーバーのポート番号（デフォルト：8000）
    debug = os.getenv("DEBUG", "True").lower() == "true"  # デバッグモードの有効/無効（デフォルト：有効）
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",  # アプリケーションの場所（このファイルのappオブジェクト）
        host=host,  # ホストアドレス
        port=port,  # ポート番号
        reload=debug  # デバッグモード時はファイル変更時の自動リロードを有効化
    )
