import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.utils.config import Config
from bot.utils.logging import logger
from bot.utils.preflight import require_firestore
from bot.services.storage import healthcheck

from bot.handlers import start, profile, analyze, generate, publish


async def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан. Укажите его в .env")

    # Firestore: обязательная проверка перед стартом бота
    require_firestore()
    if not healthcheck():
        raise RuntimeError("Firestore healthcheck failed")
    logger.info("Firestore healthcheck: OK")

    bot = Bot(
        token=Config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # 🔗 РОУТЕРЫ — вот тут их и регистрируем:
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(analyze.router)
    dp.include_router(generate.router)  # /generate + инлайн-кнопки
    dp.include_router(publish.router)   # /publish по ab_id

    logger.info("Bot starting with Firestore (strict) + A/B + publish...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
