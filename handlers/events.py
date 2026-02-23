"""Мероприятия: список и запись."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func

from database.engine import async_session_maker
from database.models import User, Event, EventRegistration
from services.user import get_user_by_telegram_id
from config import PAYMENT_PROVIDER_TOKEN

router = Router(name="events")


def user_matches_event(user: User, event: Event) -> bool:
    """Проверка: подходит ли пользователь по анкете."""
    if event.min_experience is not None and (user.driving_experience is None or user.driving_experience < event.min_experience):
        return False
    if event.moto_type and event.moto_type != "любой":
        if not user.motorcycle_type or user.motorcycle_type.lower() != event.moto_type.lower():
            return False
    if event.min_engine_capacity is not None and event.min_engine_capacity > 0:
        if user.engine_capacity is None or user.engine_capacity < event.min_engine_capacity:
            return False
    return True


async def show_events(message: Message) -> None:
    """Показать мероприятия, подходящие пользователю."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Сначала пройдите регистрацию: /start")
        return

    async with async_session_maker() as session:
        result = await session.execute(select(Event).order_by(Event.start_at.desc()))
        events = result.scalars().all()

    matching = [e for e in events if user_matches_event(user, e)]

    if not matching:
        await message.answer("Нет подходящих мероприятий. Проверьте профиль — возможно, не хватает стажа, типа мото или объёма.")
        return

    builder = InlineKeyboardBuilder()
    for e in matching:
        regs_count = 0
        async with async_session_maker() as s:
            regs_count = await s.scalar(
                select(func.count(EventRegistration.id)).where(EventRegistration.event_id == e.id)
            )
        limit = f"/{e.max_participants}" if e.max_participants else ""
        price = f"{e.price} ₽" if e.price else "Бесплатно"
        builder.row(
            InlineKeyboardButton(
                text=f"{e.name} | {price} | {regs_count}{limit}",
                callback_data=f"event:view:{e.id}",
            )
        )

    await message.answer(
        "Выберите мероприятие для записи:",
        reply_markup=builder.as_markup(),
    )


@router.message(F.text == "Мероприятия")
async def btn_events(message: Message) -> None:
    """Кнопка «Мероприятия»."""
    await show_events(message)


@router.callback_query(F.data.startswith("event:view:"))
async def event_view(callback: CallbackQuery) -> None:
    """Просмотр мероприятия и кнопка «Записаться»."""
    event_id = int(callback.data.split(":")[-1])
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Сначала пройдите регистрацию.", show_alert=True)
        return

    async with async_session_maker() as session:
        event = await session.get(Event, event_id)
        if not event:
            await callback.answer("Мероприятие не найдено.", show_alert=True)
            return

        # Уже записан?
        existing = await session.scalar(
            select(EventRegistration).where(
                EventRegistration.user_id == user.id,
                EventRegistration.event_id == event_id,
            )
        )
        if existing:
            await callback.answer("Вы уже записаны.", show_alert=True)
            return

    route = event.route_link or "—"
    price_str = f"{event.price} ₽" if event.price else "Бесплатно"
    text = (
        f"<b>{event.name}</b>\n\n"
        f"{event.description or ''}\n\n"
        f"📅 {event.start_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"📍 Маршрут: {route}\n"
        f"💰 Цена: {price_str}"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Записаться", callback_data=f"event:reg:{event_id}"),
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("event:reg:"))
async def event_register(callback: CallbackQuery) -> None:
    """Запись на мероприятие. Если платное — send_invoice."""
    event_id = int(callback.data.split(":")[-1])
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Сначала пройдите регистрацию.", show_alert=True)
        return

    async with async_session_maker() as session:
        event = await session.get(Event, event_id)
        if not event:
            await callback.answer("Мероприятие не найдено.", show_alert=True)
            return

        existing = await session.scalar(
            select(EventRegistration).where(
                EventRegistration.user_id == user.id,
                EventRegistration.event_id == event_id,
            )
        )
        if existing:
            await callback.answer("Вы уже записаны.", show_alert=True)
            return

        if event.price > 0 and PAYMENT_PROVIDER_TOKEN:
            payload = f"event:{event_id}:user:{user.id}"
            await callback.bot.send_invoice(
                chat_id=callback.message.chat.id,
                title=event.name[:32],
                description=(event.description or "")[:255] or "Участие в мероприятии",
                payload=payload,
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency="RUB",
                prices=[{"label": "Участие", "amount": event.price * 100}],
            )
            await callback.answer()
            return

        if event.price > 0 and not PAYMENT_PROVIDER_TOKEN:
            reg = EventRegistration(user_id=user.id, event_id=event_id, payment_status="pending")
            session.add(reg)
            await session.commit()
            await callback.answer("Вы записаны. Свяжитесь с организатором для оплаты.")
            await callback.message.answer(f"✅ Заявка на «{event.name}» принята. Оплата — у организатора.")
            return

        # Бесплатное — сразу записываем
        reg = EventRegistration(user_id=user.id, event_id=event_id, payment_status="paid")
        session.add(reg)
        await session.commit()

    await callback.answer("Вы записаны!")
    await callback.message.answer(
        f"✅ Вы записаны на «{event.name}».\n"
        f"📅 Старт: {event.start_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"📍 Маршрут: {event.route_link or 'уточните у организаторов'}"
    )
