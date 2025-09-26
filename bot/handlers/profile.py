from aiogram import Router, types, F
from aiogram.filters import Command
from bot.services.storage import users_col, get_user

router = Router()

@router.message(Command("profile"))
async def profile_cmd(msg: types.Message):
    user = get_user(msg.from_user.id) or {}
    p = user.get("profile", {})
    await msg.answer(
        "Профиль:\n"
        f"- Ниша: {p.get('niche')}\n"
        f"- Стиль: {p.get('style')}\n"
        f"- Аудитория: {p.get('audience')}\n\n"
        "Обновление (в одном сообщении):\n"
        "niche=<...>; style=<...>; audience=<ru/ua/kz/...>"
    )

@router.message(F.text.regexp(r"niche=|style=|audience="))
async def update_profile(msg: types.Message):
    parts = [s.strip() for s in msg.text.split(";") if "=" in s]
    entries = dict([p.split("=", 1) for p in parts])
    users_col().document(str(msg.from_user.id)).set({"profile": entries}, merge=True)
    await msg.answer("Обновлено ✅ Отправь /profile чтобы проверить.")
