from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.lim import router
from config import settings
import uvicorn

app = FastAPI(
    title="Teams会議議事録生成システム",
    description="Teams会議のトランスクリプトからAzure OpenAIを使用して議事録を自動生成するAPI",
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

app.include_router(router, prefix="/api/v1", tags=["Meeting Minutes Generation"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Teams会議議事録生成システム",
        "description": "Teams会議のトランスクリプトから議事録を自動生成",
        "docs": "/docs",
        "redoc": "/redoc",
        "azure_openai_configured": settings.azure_openai_configured,
        "endpoints": {
            "generate_minutes": "/api/v1/generate-minutes",
            "logs": "/api/v1/logs"
        }
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "service": "Teams Meeting Minutes Generator",
        "azure_openai_configured": settings.azure_openai_configured
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
