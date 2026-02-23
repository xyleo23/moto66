"""Асинхронный движок БД и функции создания таблиц."""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DATABASE_URL
from database.models import Base

# Для SQLite нужен create_async_engine с правильным URL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # True для отладки SQL-запросов
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_tables() -> None:
    """Создаёт все таблицы в БД."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_db() -> None:
    """Инициализация БД при старте бота: создание таблиц."""
    await create_tables()
