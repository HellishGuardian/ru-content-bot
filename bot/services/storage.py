from google.cloud import firestore
from google.oauth2 import service_account
from bot.utils.config import Config
from datetime import datetime, timezone

_db = None

def db():
    global _db
    if _db is None:
        creds = None
        if Config.GOOGLE_APPLICATION_CREDENTIALS:
            creds = service_account.Credentials.from_service_account_file(
                Config.GOOGLE_APPLICATION_CREDENTIALS
            )
        _db = firestore.Client(
            project=Config.FIRESTORE_PROJECT_ID,
            credentials=creds,
            database=Config.FIRESTORE_DATABASE_ID,   # <— ВАЖНО
        )
    return _db

def healthcheck() -> bool:
    """
    Минимальная проверка Firestore: set + get в служебную коллекцию.
    Бросит исключение, если нет прав/подключения.
    """
    ref = db().collection("_health").document("ping")
    ref.set({"ok": True})
    snap = ref.get()
    return bool(snap.exists and snap.to_dict().get("ok") is True)

def users_col():
    return db().collection("users")

def usage_col(user_id: int):
    return users_col().document(str(user_id)).collection("usage")

def ensure_user(user_id: int, username: str | None):
    ref = users_col().document(str(user_id))
    snap = ref.get()
    if not snap.exists:
        ref.set({
            "user_id": user_id,
            "username": username,
            "created_at": firestore.SERVER_TIMESTAMP,
            "tier": "free",
            "profile": {"niche": None, "style": "ru-playful", "audience": "ru"},
            "deleted": False,
        }, merge=True)
    else:
        ref.set({"username": username, "deleted": False}, merge=True)

def mark_deleted(user_id: int):
    users_col().document(str(user_id)).set({"deleted": True}, merge=True)

def get_user(user_id: int) -> dict | None:
    snap = users_col().document(str(user_id)).get()
    return snap.to_dict() if snap.exists else None

def log_usage(user_id: int, kind: str, meta: dict):
    now = datetime.now(timezone.utc)
    usage_col(user_id).add({
        "kind": kind,
        "meta": meta,
        "ts": now,
        "day": now.strftime("%Y-%m-%d"),
    })

def count_today(user_id: int, kind: str) -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    q = usage_col(user_id).where("day", "==", day).where("kind", "==", kind)
    return len(list(q.stream()))
