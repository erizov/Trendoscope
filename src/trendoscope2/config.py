"""
Configuration module for Trendoscope2.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from typing import Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "databases").mkdir(exist_ok=True)
(DATA_DIR / "cache").mkdir(exist_ok=True)
(DATA_DIR / "logs").mkdir(exist_ok=True)
(DATA_DIR / "temp").mkdir(exist_ok=True)

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE: Optional[str] = os.getenv('OPENAI_API_BASE')

# Anthropic Configuration
ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')

# Redis Configuration
REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
REDIS_URL: str = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
USE_REDIS: bool = os.getenv('USE_REDIS', 'true').lower() == 'true'

# Database Configuration
DATABASE_TYPE: str = os.getenv('DATABASE_TYPE', 'sqlite')
if DATABASE_TYPE == 'sqlite':
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'databases' / 'trendoscope2.db'}"
else:
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://trendoscope:trendoscope@localhost:5432/trendoscope2')

# Application Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'

# Qdrant Configuration
QDRANT_URL: str = os.getenv('QDRANT_URL', ':memory:')
QDRANT_API_KEY: Optional[str] = os.getenv('QDRANT_API_KEY')

# Local LLM Configuration
OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')

