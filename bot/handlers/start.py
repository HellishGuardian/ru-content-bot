from aiogram import Router, types
from aiogram.filters import Command
from bot.keyboards.common import main_kb
from bot.services.storage import ensure_user, mark_deleted

router = Router()

@router.message(Command("start"))
async def start_cmd(msg: types.Message):
    ensure_user(msg.from_user.id, msg.from_user.username)
    await msg.answer(
        "Привет! Я RU-content bot: анализ трендов, генерация контента и публикация.\n"
        "Профиль привязан к твоему Telegram user_id. Команды: /start /help /profile /analyze",
        reply_markup=main_kb
    )

@router.message(Command("help"))
async def help_cmd(msg: types.Message):
    await msg.answer(
        "/start — начать\n"
        "/help — помощь\n"
        "/profile — показать/обновить профиль\n"
        "/analyze — анализ (демо) с лимитом 5/день\n"
        "/delete_me — пометить профиль как удалённый\n"
        "/restore — восстановить профиль"
    )

@router.message(Command("delete_me"))
async def delete_me(msg: types.Message):
    mark_deleted(msg.from_user.id)
    await msg.answer("Профиль помечен как удалённый. Вернёшься — жми /restore.")

@router.message(Command("restore"))
async def restore(msg: types.Message):
    ensure_user(msg.from_user.id, msg.from_user.username)
    await msg.answer("Профиль восстановлен.")
