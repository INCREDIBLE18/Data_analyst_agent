"""
Configuration management module.

This module handles all application configuration including environment variables,
API keys, database paths, and LLM settings.
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # Project root directory
    ROOT_DIR: Path = Path(__file__).parent.parent
    
    # Groq Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    
    # Database Configuration
    DATABASE_PATH: Path = ROOT_DIR / os.getenv("DATABASE_PATH", "data/sales_analytics.db")
    
    # Chroma Vector DB Configuration
    CHROMA_PERSIST_DIR: Path = ROOT_DIR / os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
    CHROMA_COLLECTION_NAME: str = "database_schema"
    
    # Agent Configuration
    MAX_REPAIR_ATTEMPTS: int = int(os.getenv("MAX_REPAIR_ATTEMPTS", "3"))
    
    # Streamlit Configuration
    APP_TITLE: str = "SQL Data Analyst Agent"
    APP_ICON: str = "📊"
    
    @classmethod
    def validate(cls) -> None:
        """Validate that all required settings are present."""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please copy .env.example to .env and add your Groq API key. "
                "Get one free at: https://console.groq.com/keys"
            )
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)


# Create a singleton instance
settings = Settings()
