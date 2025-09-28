# bot/services/abtest.py
from typing import Optional
from google.cloud import firestore
from bot.services.storage import db, users_col, log_usage, get_user
from bot.services.generator import generate_variants  # ← только эта функция

def create_ab_test(user_id: int, prompt: str) -> str:
    user = get_user(user_id) or {}
    profile = user.get("profile") or {}

    # generate_variants сам сделает фолбэк на шаблоны, если n8n недоступен/пусто
    variants = generate_variants(prompt, profile)

    col = users_col().document(str(user_id)).collection("ab_tests")
    doc = col.add({
        "prompt": prompt,
        "variants": variants,
        "messages": {"A": None, "B": None},
        "selected": None,
        "status": "draft",
        "created_at": firestore.SERVER_TIMESTAMP,
    })[1]
    log_usage(user_id, "generate", {"ab_id": doc.id})
    return doc.id

def get_ab_test(user_id: int, ab_id: str) -> Optional[dict]:
    ref = users_col().document(str(user_id)).collection("ab_tests").document(ab_id)
    snap = ref.get()
    return snap.to_dict() if snap.exists else None

def set_message_id(user_id: int, ab_id: str, variant: str, message_id: int):
    users_col().document(str(user_id)).collection("ab_tests").document(ab_id)\
        .set({f"messages.{variant}": message_id}, merge=True)

def select_variant(user_id: int, ab_id: str, variant: str):
    users_col().document(str(user_id)).collection("ab_tests").document(ab_id)\
        .set({"selected": variant, "status": "selected"}, merge=True)

def mark_published(user_id: int, ab_id: str, variant: str):
    users_col().document(str(user_id)).collection("ab_tests").document(ab_id)\
        .set({
            "status": "published",
            "published_variant": variant,
            "published_at": firestore.SERVER_TIMESTAMP
        }, merge=True)

def delete_ab_test(user_id: int, ab_id: str):
    users_col().document(str(user_id)).collection("ab_tests").document(ab_id).delete()
