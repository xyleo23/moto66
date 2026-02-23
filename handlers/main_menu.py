"""Обработчики главного меню."""
from aiogram import Router, F
from aiogram.types import Message

from services.user import get_user_by_telegram_id

router = Router(name="main_menu")


@router.message(F.text == "Мой профиль")
async def btn_profile(message: Message) -> None:
    """Кнопка «Мой профиль»."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала пройдите регистрацию: /start")
        return

    cat = "Да" if user.category_a else "Нет"
    text = (
        f"<b>Ваш профиль</b>\n\n"
        f"Имя: {user.name or '—'}\n"
        f"Телефон: {user.phone or '—'}\n"
        f"Стаж: {user.driving_experience or '—'} лет\n"
        f"Тип мото: {user.motorcycle_type or '—'}\n"
        f"Объём: {user.engine_capacity or '—'} см³\n"
        f"Категория А: {cat}\n"
        f"Город: {user.city or '—'}"
    )
    await message.answer(text)
