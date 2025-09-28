from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧭 Анализ трендов"), KeyboardButton(text="✍️ Сгенерировать пост")],
        [KeyboardButton(text="📈 Опубликовать + A/B"), KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True
)

def kb_niches():
    opts = ["косметика", "таро/эзотерика", "образование/курсы", "фитнес/здоровье",
            "гаджеты/техника", "фэшн", "маркетплейсы", "другое"]
    b = InlineKeyboardBuilder()
    for o in opts: b.button(text=o, callback_data=f"niche:{o}")
    b.adjust(2,2,2,2)
    return b.as_markup()

def kb_platforms():
    opts = ["telegram", "vk", "instagram", "youtube", "rutube", "tiktok", "ozon", "wildberries"]
    b = InlineKeyboardBuilder()
    for o in opts: b.button(text=o.capitalize(), callback_data=f"platform:{o}")
    b.adjust(3,3,2)
    return b.as_markup()

def kb_styles():
    opts = ["ru-playful", "ru-expert", "ru-friendly", "ru-sales"]
    b = InlineKeyboardBuilder()
    for o in opts: b.button(text=o.replace("ru-",""), callback_data=f"style:{o}")
    b.adjust(2,2)
    return b.as_markup()

def kb_skip():
    b = InlineKeyboardBuilder()
    b.add(InlineKeyboardButton(text="Пропустить", callback_data="skip"))
    return b.as_markup()