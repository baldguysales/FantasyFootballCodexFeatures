from pydantic_settings import BaseSettings
from pydantic import validator, EmailStr, HttpUrl
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256") 
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/ff_codex")
    
    # Security
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Redis (for future use)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # OpenAI (for future use)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
