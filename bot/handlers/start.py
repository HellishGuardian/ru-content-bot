from aiogram import Router, types
from aiogram.filters import Command
from bot.keyboards.common import main_kb

router = Router()

@router.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "Привет! Я RU-content bot: анализ трендов, генерация контента и публикация.\n"
        "Пока что запущен минимальный режим. Команды: /start /help",
        reply_markup=main_kb
    )

@router.message(Command("help"))
async def help_cmd(msg: types.Message):
    await msg.answer(
        "/start — начать\n"
        "/help — помощь\n\n"
        "Скоро добавим: профили, квоты, A/B и публикацию."
    )
