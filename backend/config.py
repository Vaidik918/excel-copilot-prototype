import os
from dotenv import load_dotenv

# Explicitly load .env from this directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", True)
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-change-in-production")

    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/temp")
    ALLOWED_EXTENSIONS = {"xlsx", "xls"}

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0.2))
    GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", 1000))

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

def get_config():
    return Config()

config = get_config()
