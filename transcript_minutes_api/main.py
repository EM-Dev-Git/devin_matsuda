from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from modules.database import create_tables
from modules.logger import logger
from routers import auth, transcript

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up transcript-to-meeting-minutes API")
    create_tables()
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down transcript-to-meeting-minutes API")

app = FastAPI(
    title="Transcript to Meeting Minutes API",
    description="API for generating meeting minutes from transcripts using OpenAI GPT",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transcript.router)

@app.get("/")
async def root():
    return {
        "message": "Transcript to Meeting Minutes API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
