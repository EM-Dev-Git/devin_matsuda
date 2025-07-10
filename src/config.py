from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    @property
    def azure_openai_configured(self) -> bool:
        return all([
            self.AZURE_OPENAI_API_KEY,
            self.AZURE_OPENAI_ENDPOINT,
            self.AZURE_OPENAI_DEPLOYMENT_NAME
        ])
    
    class Config:
        env_file = "../env/.env"
        env_file_encoding = "utf-8"


settings = Settings()
