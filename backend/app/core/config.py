"""Application configuration using Pydantic Settings."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for EarthScope backend."""
    
    PROJECT_NAME: str = "EarthScope API"
    VERSION: str = "0.6.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    RAW_DATA_DIR: Path = BASE_DIR / "datasets"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    METADATA_DIR: Path = BASE_DIR / "data" / "metadata"
    MODELS_DIR: Path = BASE_DIR / "data" / "models"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
