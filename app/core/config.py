from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    class config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
settings = Settings()
    