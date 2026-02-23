"""
Точка входа moto66 — Telegram-бот для мотолюбителей.
aiogram 3.x + SQLAlchemy 2.0 (aiosqlite).
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, SUPERADMIN_ID
from database import init_db
from handlers import main_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота."""
    logger.info("Создание таблиц БД...")
    await init_db()
    logger.info("Бот запущен. Superadmin ID: %s", SUPERADMIN_ID)


async def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в .env")

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(on_startup)
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
