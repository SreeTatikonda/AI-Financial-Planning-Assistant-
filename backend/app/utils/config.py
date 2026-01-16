"""
Configuration settings for the AI Financial Planning Agent
Uses Pydantic settings for environment variable management
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Financial Planning Agent"
    DEBUG: bool = False
    
    # LLM Configuration
    LLM_PROVIDER: str = "gemini"  # Options: "gemini", "ollama"
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    
    # Database
    DATABASE_URL: str = "sqlite:///./financial_agent.db"
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # API Keys for Financial Data
    ALPHA_VANTAGE_API_KEY: str = ""  # Optional: for stock data
    
    # Agent Configuration
    MAX_ITERATIONS: int = 5
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
