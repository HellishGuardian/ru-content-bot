from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.services.storage import ensure_user, update_profile

router = Router()

def parse_kv(s: str) -> dict:
    out = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k,v = part.split("=",1)
            out[k.strip().lower()] = v.strip()
    return out

@router.message(Command("profile"))
async def profile_cmd(msg: Message):
    user = ensure_user(msg.from_user.id)
    args = (msg.text or "").split(" ",1)
    if len(args) == 1:
        p = user.get("profile", {})
        await msg.answer(
            "Профиль:\n"
            f"- about: {p.get('about')}\n"
            f"- platform: {p.get('platform')}\n"
            f"- style: {p.get('style')}\n"
            f"- audience: {p.get('audience')}\n\n"
            "Изменить: /profile about=...; platform=telegram|vk|instagram|youtube|rutube|tiktok|ozon|wildberries; "
            "style=ru-playful|ru-expert|ru-friendly|ru-sales; audience=..."
        )
        return
    data = parse_kv(args[1])
    new_prof = {**(user.get("profile") or {}), **data}
    update_profile(msg.from_user.id, new_prof)
    await msg.answer("Профиль обновлён ✅")
