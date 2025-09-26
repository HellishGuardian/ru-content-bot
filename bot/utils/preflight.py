from pathlib import Path
from .config import Config

def require_firestore():
    """
    Выкидывает RuntimeError, если Firestore не готов.
    """
    cred = (Config.GOOGLE_APPLICATION_CREDENTIALS or "").strip()
    if not Config.FIRESTORE_PROJECT_ID:
        raise RuntimeError("FIRESTORE_PROJECT_ID is missing in .env")
    if not cred:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is missing in .env")
    if not Path(cred).exists():
        raise RuntimeError(f"Credentials file not found at {cred}")
