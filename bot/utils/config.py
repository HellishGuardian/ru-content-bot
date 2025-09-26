import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]  # .../ru-content-bot
ENV_PATH = ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def _list(env_key: str) -> list[int]:
    raw = os.getenv(env_key, "")
    return [int(x.strip()) for x in raw.split(",") if x.strip()]

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ENV = os.getenv("ENV", "dev")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID")
    FIRESTORE_DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID", "(default)")  # <— НОВОЕ
    FREE_ANALYSES_PER_DAY = int(os.getenv("FREE_ANALYSES_PER_DAY", "5"))
    ADMIN_IDS = set(_list("ADMIN_IDS"))
    N8N_WEBHOOK_BASE = (os.getenv("N8N_WEBHOOK_BASE") or "").rstrip("/")
