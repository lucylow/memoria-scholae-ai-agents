"""
Configuration settings for MemoriaScholae backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MemMachine Configuration
    memmachine_url: str = "http://localhost:8080"
    memmachine_api_key: Optional[str] = None
    
    # Neo4j Configuration
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    log_level: str = "INFO"
    
    # Application Settings
    max_upload_size: int = 52428800  # 50MB
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
