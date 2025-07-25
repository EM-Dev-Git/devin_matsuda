from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Transcript to Minutes API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    database_url: str = "sqlite:///./app.db"
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    
    microsoft_tenant_id: str
    microsoft_client_id: str
    microsoft_client_secret: str
    microsoft_graph_scopes: str = "https://graph.microsoft.com/.default"
    
    log_level: str = "INFO"
    log_file: str = "app.log"

    class Config:
        env_file = ".env"


settings = Settings()
