from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from google.cloud import firestore
from google.oauth2 import service_account

from bot.utils.config import Config

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
            database=Config.FIRESTORE_DATABASE_ID,
        )
    return _db


def users_col():
    return db().collection("users")


def usage_col(user_id: int):
    return users_col().document(str(user_id)).collection("usage")


def healthcheck() -> bool:
    ref = db().collection("_health").document("ping")
    ref.set({"ok": True})
    snap = ref.get()
    return bool(snap.exists and snap.to_dict().get("ok") is True)


def ensure_user(user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
    """
    Создаёт документ пользователя при отсутствии.
    Возвращает словарь пользователя (как в БД).
    """
    ref = users_col().document(str(user_id))
    snap = ref.get()
    if not snap.exists:
        doc = {
            "user_id": user_id,
            "username": username,
            "created_at": firestore.SERVER_TIMESTAMP,
            "tier": "free",
            "profile": {},  # пустой профиль — будем заполнять
            "deleted": False,
        }
        ref.set(doc, merge=True)
        return doc

    if username is not None:
        ref.set({"username": username, "deleted": False}, merge=True)

    data = snap.to_dict() or {}
    data.setdefault("profile", {})
    return data


def update_profile(user_id: int, data: Dict[str, Any]):
    users_col().document(str(user_id)).set({"profile": data}, merge=True)


def get_user(user_id: int) -> dict | None:
    snap = users_col().document(str(user_id)).get()
    return snap.to_dict() if snap.exists else None


def mark_deleted(user_id: int):
    users_col().document(str(user_id)).set({"deleted": True}, merge=True)


def log_usage(user_id: int, kind: str, meta: dict):
    now = datetime.now(timezone.utc)
    usage_col(user_id).add(
        {"kind": kind, "meta": meta, "ts": now, "day": now.strftime("%Y-%m-%d")}
    )


def count_today(user_id: int, kind: str) -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    q = usage_col(user_id).where("day", "==", day).where("kind", "==", kind)
    return len(list(q.stream()))


def missing_profile_fields(user_doc: Dict[str, Any]) -> list[str]:
    """
    На будущее: какие поля профиля ещё не заполнены.
    Для нашего свободного онбординга считаем основными:
    about, platform, style, audience.
    """
    need = ["about", "platform", "style", "audience"]
    prof = (user_doc or {}).get("profile", {})
    return [f for f in need if not prof.get(f)]
