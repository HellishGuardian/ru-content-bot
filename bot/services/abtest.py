from datetime import datetime, timezone
from google.cloud import firestore
from bot.services.storage import db, users_col, log_usage, get_user

def _variants_from_prompt(prompt: str, profile: dict | None):
    style = (profile or {}).get("style") or "ru-playful"
    audience = (profile or {}).get("audience") or "ru"
    # Простые 2 варианта — позже заменим на GigaChat/Kandinsky.
    a = (
        f"🔥 {prompt}\n\n"
        f"Короткий лид + буллеты.\n"
        f"• Факт/выгода #1\n• Факт/выгода #2\n• Призыв к действию.\n"
        f"Тон: {style}, аудитория: {audience}."
    )
    b = (
        f"🧪 {prompt}\n\n"
        f"Хук-вопрос + мини-история, 1 абзац.\n"
        f"В конце — явный CTA и эмодзи.\n"
        f"Тон: {style}, аудитория: {audience}."
    )
    # На будущее сюда воткнём простую «предикцию» (скор).
    return {
        "A": {"text": a, "pred": 0.52},
        "B": {"text": b, "pred": 0.56},
    }

def create_ab_test(user_id: int, prompt: str) -> str:
    user = get_user(user_id) or {}
    profile = user.get("profile") or {}
    variants = _variants_from_prompt(prompt, profile)
    col = users_col().document(str(user_id)).collection("ab_tests")
    doc = col.add({
        "prompt": prompt,
        "variants": variants,
        "selected": None,
        "status": "draft",
        "created_at": firestore.SERVER_TIMESTAMP,
    })[1]  # returns (update_time, doc_ref)
    log_usage(user_id, "generate", {"ab_id": doc.id})
    return doc.id

def get_ab_test(user_id: int, ab_id: str) -> dict | None:
    ref = users_col().document(str(user_id)).collection("ab_tests").document(ab_id)
    snap = ref.get()
    return snap.to_dict() if snap.exists else None

def select_variant(user_id: int, ab_id: str, variant: str):
    ref = users_col().document(str(user_id)).collection("ab_tests").document(ab_id)
    ref.set({"selected": variant, "status": "selected"}, merge=True)
