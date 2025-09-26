from bot.services.storage import count_today, get_user
from bot.utils.config import Config

def can_analyze(user_id: int) -> tuple[bool, str]:
    user = get_user(user_id) or {}
    tier = user.get("tier", "free")
    limit = 999999 if tier == "pro" else Config.FREE_ANALYSES_PER_DAY
    used = count_today(user_id, "analyze")
    if used >= limit:
        return False, f"Лимит на сегодня исчерпан ({used}/{limit}). Оформите PRO, чтобы без ограничений."
    left = limit - used
    return True, f"Доступно сегодня: {left} анализ(ов)."
