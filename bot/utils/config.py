import os
from pathlib import Path
from dotenv import load_dotenv

# Явно грузим .env из корня репозитория, чтобы не зависеть от текущей папки запуска
ROOT = Path(__file__).resolve().parents[2]  # .../ru-content-bot
ENV_PATH = ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ENV = os.getenv("ENV", "dev")
