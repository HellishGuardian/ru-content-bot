import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.utils.config import Config
from bot.utils.logging import logger
from bot.utils.preflight import require_firestore
from bot.services.storage import healthcheck
from bot.handlers import start, profile, analyze

async def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан. Укажите его в .env")

    # Обязательная проверка Firestore до старта бота
    require_firestore()
    try:
        ok = healthcheck()
        if not ok:
            raise RuntimeError("Firestore healthcheck failed (doc not readable)")
        logger.info("Firestore healthcheck: OK")
    except Exception as e:
        raise RuntimeError(f"Firestore healthcheck error: {e}") from e

    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(analyze.router)
    logger.info("Bot starting with Firestore (strict mode)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
