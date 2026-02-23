"""SOS: рассылка всем пользователям, кнопка «Еду на помощь»."""
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Location
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from config import SUPERADMIN_ID
from database.engine import async_session_maker
from database.models import User, SosSignal
from services.user import get_user_by_telegram_id
from states.sos import SosStates
from keyboards.sos import (
    get_sos_problem_keyboard,
    get_location_keyboard,
    get_skip_description_keyboard,
    get_help_button_keyboard,
)

router = Router(name="sos")


async def start_sos(message: Message, state: FSMContext) -> None:
    """Начать SOS."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала пройдите регистрацию: /start")
        return

    await state.set_state(SosStates.problem_type)
    await state.update_data(user_id=user.id, user_name=user.name or "Без имени", user_phone=user.phone or "—")
    await message.answer("Выберите тип проблемы:", reply_markup=get_sos_problem_keyboard())


@router.message(F.text == "Кнопка SOS 🆘")
async def btn_sos(message: Message, state: FSMContext) -> None:
    """Кнопка «SOS»."""
    await start_sos(message, state)


@router.callback_query(SosStates.problem_type, F.data.startswith("sos:"))
async def sos_problem_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Выбран тип проблемы."""
    problem = callback.data.split(":", 1)[1]
    await state.update_data(problem_type=problem)
    await state.set_state(SosStates.location)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Отправьте вашу геопозицию:",
        reply_markup=get_location_keyboard(),
    )
    await callback.answer()


@router.message(SosStates.location, F.location)
async def sos_location(message: Message, state: FSMContext) -> None:
    """Геолокация получена."""
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(latitude=lat, longitude=lon)
    await state.set_state(SosStates.description)
    await message.answer(
        "Краткое описание (или нажмите «Пропустить»):",
        reply_markup=get_skip_description_keyboard(),
    )


@router.callback_query(SosStates.description, F.data == "sos_skip_desc")
async def sos_skip_desc(callback: CallbackQuery, state: FSMContext) -> None:
    """Пропуск описания."""
    await state.update_data(description="")
    await _finish_sos(callback.message, state, callback.bot)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.message(SosStates.description, F.text)
async def sos_description(message: Message, state: FSMContext) -> None:
    """Описание введено."""
    await state.update_data(description=message.text.strip()[:500])
    await _finish_sos(message, state, message.bot)


async def _finish_sos(message: Message, state: FSMContext, bot) -> None:
    """Сохранить SOS и разослать всем."""
    data = await state.get_data()
    await state.clear()

    async with async_session_maker() as session:
        sos = SosSignal(
            user_id=data["user_id"],
            problem_type=data["problem_type"],
            description=data.get("description", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )
        session.add(sos)
        await session.commit()
        await session.refresh(sos)

    name = data.get("user_name", "Без имени")
    problem = data.get("problem_type", "—")
    desc = data.get("description") or "—"
    phone = data.get("user_phone", "—")

    text = (
        f"🆘 <b>Нужна помощь!</b>\n\n"
        f"Имя: {name}\n"
        f"Проблема: {problem}\n"
        f"Описание: {desc}\n"
        f"Телефон: {phone}"
    )

    # Рассылка всем пользователям
    async with async_session_maker() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = [r[0] for r in result.fetchall()]

    for uid in user_ids:
        try:
            if data.get("latitude") is not None and data.get("longitude") is not None:
                await bot.send_location(uid, data["latitude"], data["longitude"])
            await bot.send_message(
                uid,
                text,
                reply_markup=get_help_button_keyboard(sos.id),
            )
        except Exception:
            pass
        await asyncio.sleep(0.05)

    # Дубликат СуперАдмину
    try:
        if SUPERADMIN_ID and SUPERADMIN_ID not in user_ids:
            if data.get("latitude") is not None:
                await bot.send_location(SUPERADMIN_ID, data["latitude"], data["longitude"])
            await bot.send_message(
                SUPERADMIN_ID,
                f"[SOS] {text}",
                reply_markup=get_help_button_keyboard(sos.id),
            )
    except Exception:
        pass

    await message.answer("SOS отправлен. Ожидайте помощи.")


@router.callback_query(F.data.startswith("sos_help:"))
async def sos_help_clicked(callback: CallbackQuery) -> None:
    """Кнопка «Еду на помощь» — уведомить инициатора SOS."""
    sos_id = int(callback.data.split(":")[1])
    rescuer = await get_user_by_telegram_id(callback.from_user.id)
    if not rescuer:
        await callback.answer("Сначала зарегистрируйтесь.", show_alert=True)
        return

    async with async_session_maker() as session:
        sos = await session.get(SosSignal, sos_id)
        if not sos:
            await callback.answer("SOS не найден.", show_alert=True)
            return
        initiator = await session.get(User, sos.user_id)

    if not initiator:
        await callback.answer("Инициатор не найден.", show_alert=True)
        return

    rescuer_name = rescuer.name or callback.from_user.full_name or "Спасатель"
    contact = rescuer.phone or f"tg://user?id={callback.from_user.id}"

    try:
        await callback.bot.send_message(
            initiator.telegram_id,
            f"✅ {rescuer_name} выехал на помощь!\nЕго контакт: {contact}",
        )
    except Exception:
        pass

    await callback.answer("Инициатор уведомлён.")
