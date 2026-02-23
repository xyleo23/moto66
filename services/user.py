"""Сервис пользователей."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_maker
from database.models import User


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """Получить пользователя по Telegram ID."""
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()


async def create_user(
    telegram_id: int,
    name: str | None = None,
    phone: str | None = None,
    driving_experience: int | None = None,
    motorcycle_type: str | None = None,
    engine_capacity: int | None = None,
    category_a: bool = False,
    city: str | None = None,
    role: str = "user",
) -> User:
    """Создать пользователя."""
    async with async_session_maker() as session:
        user = User(
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            driving_experience=driving_experience,
            motorcycle_type=motorcycle_type,
            engine_capacity=engine_capacity,
            category_a=category_a,
            city=city,
            role=role,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user(session: AsyncSession, user: User, **kwargs) -> User:
    """Обновить поля пользователя."""
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user
