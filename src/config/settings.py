"""
Centralized configuration settings for Adaptive Code Lab.
All environment variables are loaded here to provide a single source of truth.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = os.getenv("ACCL_DB_PATH", f"sqlite:///{DATA_DIR / 'Accl_DB.db'}")

# Flask configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

# AI configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")

# Plagiarism detection
PLAGIARISM_THRESHOLD = float(os.getenv("PLAGIARISM_THRESHOLD", "0.85"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))

# Sandbox configuration
SANDBOX_PATH = os.getenv("SANDBOX_PATH", "./sandbox")
SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "5"))
SANDBOX_MEMORY_LIMIT_MB = int(os.getenv("SANDBOX_MEMORY_LIMIT_MB", "256"))

# Environment
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
