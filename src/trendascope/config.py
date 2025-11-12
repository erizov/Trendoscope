"""
Configuration module for Trendoscope.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from typing import Optional

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars


# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE: Optional[str] = os.getenv('OPENAI_API_BASE')

# Anthropic Configuration
ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')

# LiveJournal Configuration
LJ_USERNAME: Optional[str] = os.getenv('LJ_USERNAME')
LJ_PASSWORD: Optional[str] = os.getenv('LJ_PASSWORD')

# Redis Configuration
REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Qdrant Configuration
QDRANT_URL: str = os.getenv('QDRANT_URL', ':memory:')
QDRANT_API_KEY: Optional[str] = os.getenv('QDRANT_API_KEY')

# Local LLM Configuration
OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')

# Application Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

