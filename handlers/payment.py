"""Обработчики оплаты (Telegram Invoices / ЮKassa)."""
from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from sqlalchemy import select

from config import SUPERADMIN_ID
from database.engine import async_session_maker
from database.models import User, Event, EventRegistration

router = Router(name="payment")


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery) -> None:
    """Подтверждение готовности принять платёж."""
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    """Успешная оплата — запись в EventRegistration, уведомление пользователю и админу."""
    payment = message.successful_payment
    payload = payment.invoice_payload

    # payload: "event:{event_id}:user:{user_id}"
    parts = payload.split(":")
    if len(parts) != 4 or parts[0] != "event" or parts[2] != "user":
        return
    event_id = int(parts[1])
    user_db_id = int(parts[3])

    async with async_session_maker() as session:
        user = await session.get(User, user_db_id)
        event = await session.get(Event, event_id)
        if not user or not event:
            return

        reg = EventRegistration(
            user_id=user.id,
            event_id=event.id,
            payment_status="paid",
        )
        session.add(reg)
        await session.commit()

    # Подтверждение пользователю
    await message.answer(
        f"✅ Оплата получена! Вы записаны на «{event.name}».\n\n"
        f"📅 Старт: {event.start_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"📍 Маршрут: {event.route_link or 'уточните у организаторов'}\n"
        f"💰 Сумма: {payment.total_amount // 100} ₽"
    )

    # Уведомление СуперАдмину
    try:
        await message.bot.send_message(
            SUPERADMIN_ID,
            f"💰 Новая оплата!\n"
            f"Мероприятие: {event.name}\n"
            f"Участник: {user.name or user.telegram_id}\n"
            f"Сумма: {payment.total_amount // 100} ₽",
        )
    except Exception:
        pass
