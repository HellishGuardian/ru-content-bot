import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.utils.config import Config
from bot.utils.logging import logger
from bot.handlers import start

async def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан. Укажите его в .env")
    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(start.router)
    logger.info("Bot starting (minimal)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
