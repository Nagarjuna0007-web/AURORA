from pathlib import Path
import os

from dotenv import load_dotenv

# --------------------------------------------------
# Project Root Directory
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------
# Application Configuration
# --------------------------------------------------
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
APP_NAME = os.getenv("APP_NAME", "AURORA")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
CONTEXT_WINDOW = int(os.getenv("CONTEXT_WINDOW", "10"))
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or None