from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str
    
    API_V1_STR: str = Field("/api/v1", description="API prefix path")

    class Config:
        env_file = ".env"

        
settings = Settings()
    