from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.lim import router
from config import settings
import uvicorn

app = FastAPI(
    title="AI質問応答システム",
    description="Azure OpenAIを使用したプロンプトベースの質問応答API",
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

app.include_router(router, prefix="/api/v1", tags=["AI Question Answering"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "AI質問応答システム",
        "docs": "/docs",
        "redoc": "/redoc",
        "azure_openai_configured": settings.azure_openai_configured
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "azure_openai_configured": settings.azure_openai_configured
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
