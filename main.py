from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, minutes
from database import create_tables
from modules.logger import api_logger
import uvicorn
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Teams会議議事録生成API",
    description="Teams会議のトランスクリプトからOpenAIを使用して議事録を自動生成するAPI。JWT認証とログ機能を含む。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(minutes.router, prefix="/minutes", tags=["Meeting Minutes"])

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("Starting Teams Meeting Minutes API...")
    create_tables()
    logger.info("Database tables created/verified")
    logger.info("Teams Meeting Minutes API started successfully")

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Teams会議議事録生成API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth (login, register)",
            "minutes": "/minutes (generate - JWT required)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "Teams Meeting Minutes API"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
