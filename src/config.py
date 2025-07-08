import os
from dotenv import load_dotenv

load_dotenv("../env/.env")


class Settings:
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    @property
    def azure_openai_configured(self) -> bool:
        return bool(self.AZURE_OPENAI_API_KEY and self.AZURE_OPENAI_ENDPOINT)


settings = Settings()
