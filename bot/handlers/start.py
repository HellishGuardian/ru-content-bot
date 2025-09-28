from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.utils.forms import Onboarding
from bot.services.storage import ensure_user, update_profile

router = Router()

@router.message(Command("start"))
async def start_cmd(msg: Message, state: FSMContext):
    ensure_user(msg.from_user.id)
    await msg.answer(
        "Привет! Я RU-content bot: анализ трендов, генерация и публикация.\n"
        "Чтобы персонализировать тексты, напиши 1–2 предложения про себя:\n"
        "— ниша/чем занимаешься (например: таро, косметика, продюсер)\n"
        "— основная площадка (tg/vk/instagram/youtube и т.п.)\n"
        "— стиль, аудитория (например: экспертно; женщины 18–35)\n\n"
        "Пример: «Я веду инстаграм про косметику, стиль — дружелюбный, аудитория женщины 18–35»."
    )
    await state.set_state(Onboarding.about)

@router.message(Onboarding.about)
async def save_about(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    if len(text) < 10:
        await msg.answer("Слишком коротко. Напиши 1–2 предложения (минимум 10 символов).")
        return

    # простая эвристика: вытащим платформу/стиль/аудиторию, остальное кладём в about
    low = text.lower()
    platform = next((p for p in ["telegram","tg","vk","instagram","insta","youtube","rutube","tiktok","ozon","wildberries"]
                     if p in low), "telegram")
    style = "ru-friendly"
    if any(w in low for w in ["эксперт", "строг"]): style = "ru-expert"
    if any(w in low for w in ["игрив", "фанов"]):   style = "ru-playful"
    if any(w in low for w in ["продающ", "sales"]): style = "ru-sales"

    # аудитория, если указали диапазон
    import re
    m = re.search(r'(\d{2})\s*[-–]\s*(\d{2})', low)
    audience = f"{m.group(1)}-{m.group(2)}" if m else "ru"

    profile = {
        "about": text,             # свободный текст пользователя
        "platform": {"tg":"telegram","insta":"instagram"}.get(platform, platform),
        "style": style,
        "audience": audience,
    }
    update_profile(msg.from_user.id, profile)
    await state.clear()
    await msg.answer(
    "Готово! Профиль сохранён ✅\n"
    "Теперь можно: /generate «тема»\n"
    "Например: /generate хук для продажи iPhone 16 (базовая версия)"
)

