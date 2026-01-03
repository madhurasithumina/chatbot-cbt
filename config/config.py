"""
Configuration management for CBT Chatbot
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "CBT Mental Health Chatbot"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    
    # Database
    database_url: str = "sqlite:///./data/chatbot.db"
    redis_url: Optional[str] = None
    
    # Models
    custom_model_path: str = "./data/models/cbt_model"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_context_length: int = 2048
    
    # Hybrid Response Configuration
    custom_model_weight: float = 0.4
    gpt_model_weight: float = 0.6
    confidence_threshold: float = 0.7
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/chatbot.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
