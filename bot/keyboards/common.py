from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧭 Анализ трендов"), KeyboardButton(text="✍️ Сгенерировать пост")],
        [KeyboardButton(text="📈 Опубликовать + A/B"), KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True
)
