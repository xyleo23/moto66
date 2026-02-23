"""Заявка на двойку (поездка с пассажиром)."""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from config import (
    SUPERADMIN_ID,
    DOUBLE_REQUESTS_CHAT_ID,
    DOUBLE_MIN_EXPERIENCE,
    DOUBLE_MIN_ENGINE_CAPACITY,
    DOUBLE_FORBIDDEN_MOTO_TYPE,
)
from database.engine import async_session_maker
from database.models import User, DoubleRequest
from services.user import get_user_by_telegram_id
from states.double import DoubleRequestStates

router = Router(name="double")


def check_double_requirements(user: User) -> tuple[bool, str]:
    """
    Проверка анкеты для заявки на двойку.
    Возвращает (ok, reason).
    """
    if user.driving_experience is None or user.driving_experience < DOUBLE_MIN_EXPERIENCE:
        return False, f"Для перевозки двоек ваш стаж должен быть более {DOUBLE_MIN_EXPERIENCE} лет."
    if user.engine_capacity is None or user.engine_capacity < DOUBLE_MIN_ENGINE_CAPACITY:
        return False, f"Для перевозки двоек объём двигателя должен быть не менее {DOUBLE_MIN_ENGINE_CAPACITY} см³."
    if user.motorcycle_type and user.motorcycle_type.lower() == DOUBLE_FORBIDDEN_MOTO_TYPE.lower():
        return False, f"Для перевозки двоек тип мотоцикла не должен быть «{DOUBLE_FORBIDDEN_MOTO_TYPE}»."
    return True, ""


async def start_double_request(message: Message, state: FSMContext) -> None:
    """Начать заявку на двойку."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала пройдите регистрацию: /start")
        return

    ok, reason = check_double_requirements(user)
    if not ok:
        await message.answer(f"Извините, {reason}")
        return

    await state.set_state(DoubleRequestStates.date_route)
    await message.answer("Введите дату и маршрут поездки (например: 20.03.2025, Москва — Тула):")


@router.message(F.text == "Заявка на двойку")
async def btn_double(message: Message, state: FSMContext) -> None:
    """Кнопка «Заявка на двойку»."""
    await start_double_request(message, state)


@router.message(DoubleRequestStates.date_route, F.text)
async def process_date_route(message: Message, state: FSMContext) -> None:
    """Сохранить заявку и опубликовать в канал/чат."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await state.clear()
        return

    date_route = message.text.strip()
    async with async_session_maker() as session:
        dr = DoubleRequest(user_id=user.id, date_route=date_route)
        session.add(dr)
        await session.commit()

    await state.clear()

    text = (
        f"🛵 <b>Заявка на двойку</b>\n\n"
        f"Водитель: {user.name or 'Без имени'}\n"
        f"Дата/маршрут: {date_route}\n"
        f"Контакты: {user.phone or 'в профиле'}"
    )

    if DOUBLE_REQUESTS_CHAT_ID:
        try:
            await message.bot.send_message(
                chat_id=DOUBLE_REQUESTS_CHAT_ID,
                text=text,
            )
        except Exception:
            pass

    await message.answer("Заявка создана и опубликована.")
