"""Админ-панель. Доступ только для SuperAdmin."""
import asyncio
from datetime import datetime
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func

from config import SUPERADMIN_ID
from database.engine import async_session_maker
from database.models import User, Event, EventRegistration, SosSignal
from keyboards.main_menu import get_main_keyboard
from keyboards.admin import get_admin_keyboard, get_moto_type_event_keyboard, get_back_to_admin_keyboard
from states.event import EventCreationStates
from states.broadcast import BroadcastStates

router = Router(name="admin")


def is_superadmin(user_id: int) -> bool:
    return user_id == SUPERADMIN_ID


@router.message(Command("admin"))
@router.message(F.text == "👑 Админ-панель")
async def cmd_admin(message: Message, state: FSMContext) -> None:
    """Команда /admin."""
    await state.clear()
    if not is_superadmin(message.from_user.id):
        await message.answer("Доступ запрещён.")
        return
    await message.answer("Панель администратора:", reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery, state: FSMContext) -> None:
    """Назад в админку."""
    await state.clear()
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return
    await callback.message.edit_text("Панель администратора:", reply_markup=get_admin_keyboard())
    await callback.answer()


# ---------- Создание мероприятия ----------
@router.callback_query(F.data == "admin:create_event")
async def start_create_event(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать создание мероприятия."""
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return
    await state.set_state(EventCreationStates.name)
    await callback.message.edit_text("Введите название мероприятия:")
    await callback.answer()


@router.message(EventCreationStates.name, F.text)
async def event_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip()[:200])
    await state.set_state(EventCreationStates.description)
    await message.answer("Введите описание:")


@router.message(EventCreationStates.description, F.text)
async def event_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip())
    await state.set_state(EventCreationStates.date_place)
    await message.answer("Введите дату и место (например: 15.03.2025 10:00, Москва):")


@router.message(EventCreationStates.date_place, F.text)
async def event_date_place(message: Message, state: FSMContext) -> None:
    await state.update_data(date_place=message.text.strip())
    await state.set_state(EventCreationStates.route)
    await message.answer("Введите ссылку на маршрут (или «нет»):")


@router.message(EventCreationStates.route, F.text)
async def event_route(message: Message, state: FSMContext) -> None:
    text = message.text.strip().lower()
    route = None if text in ("нет", "—", "-") else message.text.strip()[:500]
    await state.update_data(route=route)
    await state.set_state(EventCreationStates.price)
    await message.answer("Цена участия (руб, 0 = бесплатно):")


@router.message(EventCreationStates.price, F.text.regexp(r"^\d+$"))
async def event_price(message: Message, state: FSMContext) -> None:
    await state.update_data(price=int(message.text))
    await state.set_state(EventCreationStates.max_participants)
    await message.answer("Максимальное количество участников (0 = без лимита):")


@router.message(EventCreationStates.max_participants, F.text.regexp(r"^\d+$"))
async def event_max_participants(message: Message, state: FSMContext) -> None:
    await state.update_data(max_participants=int(message.text))
    await state.set_state(EventCreationStates.min_experience)
    await message.answer("Минимальный стаж вождения (лет, 0 = не важно):")


@router.message(EventCreationStates.min_experience, F.text.regexp(r"^\d+$"))
async def event_min_experience(message: Message, state: FSMContext) -> None:
    await state.update_data(min_experience=int(message.text))
    await state.set_state(EventCreationStates.moto_type)
    await message.answer("Требуемый тип мотоцикла:", reply_markup=get_moto_type_event_keyboard())


@router.callback_query(EventCreationStates.moto_type, F.data.startswith("emoto:"))
async def event_moto_type(callback: CallbackQuery, state: FSMContext) -> None:
    moto = callback.data.split(":", 1)[1]
    await state.update_data(moto_type=moto if moto != "любой" else None)
    await state.set_state(EventCreationStates.min_engine_capacity)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Минимальный объём двигателя (см³, 0 = не важно):")
    await callback.answer()


@router.message(EventCreationStates.min_engine_capacity, F.text.regexp(r"^\d+$"))
async def event_min_capacity(message: Message, state: FSMContext) -> None:
    await state.update_data(min_engine_capacity=int(message.text))

    data = await state.get_data()
    # Парсим дату: "15.03.2025 10:00" или "2025-03-15 10:00"
    date_str = data.get("date_place", "")
    start_at = datetime.now()
    try:
        for fmt in ("%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%d.%m.%Y"):
            try:
                start_at = datetime.strptime(date_str[:16], fmt)
                break
            except ValueError:
                continue
    except Exception:
        pass

    async with async_session_maker() as session:
        event = Event(
            name=data["name"],
            description=data.get("description"),
            start_at=start_at,
            route_link=data.get("route"),
            price=data.get("price", 0),
            max_participants=data.get("max_participants", 0),
            min_experience=data.get("min_experience") or None,
            moto_type=data.get("moto_type"),
            min_engine_capacity=data.get("min_engine_capacity") or None,
        )
        session.add(event)
        await session.commit()

    await state.clear()
    await message.answer(f"Мероприятие «{event.name}» создано.", reply_markup=get_main_keyboard())


# ---------- Статистика ----------
@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery) -> None:
    """Статистика."""
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return

    async with async_session_maker() as session:
        users_count = await session.scalar(select(func.count(User.id)))
        events_count = await session.scalar(select(func.count(Event.id)))
        regs_count = await session.scalar(select(func.count(EventRegistration.id)))
        sos_count = await session.scalar(select(func.count(SosSignal.id)))

    text = (
        f"<b>Статистика</b>\n\n"
        f"👥 Пользователей: {users_count}\n"
        f"📅 Мероприятий: {events_count}\n"
        f"📝 Заявок на мероприятия: {regs_count}\n"
        f"🆘 SOS-сигналов: {sos_count}"
    )
    await callback.message.edit_text(text, reply_markup=get_back_to_admin_keyboard())
    await callback.answer()


# ---------- Рассылка ----------
@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать рассылку."""
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return
    await state.set_state(BroadcastStates.message)
    await callback.message.edit_text(
        "Отправьте сообщение для рассылки (текст, фото или видео):",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


@router.message(BroadcastStates.message, F.photo)
async def broadcast_photo(message: Message, state: FSMContext) -> None:
    """Рассылка: фото."""
    await state.update_data(
        content_type="photo",
        file_id=message.photo[-1].file_id,
        caption=message.caption or "",
    )
    await state.set_state(BroadcastStates.confirm)
    await message.answer("Начать рассылку? (да/нет)")


@router.message(BroadcastStates.message, F.video)
async def broadcast_video(message: Message, state: FSMContext) -> None:
    """Рассылка: видео."""
    await state.update_data(
        content_type="video",
        file_id=message.video.file_id,
        caption=message.caption or "",
    )
    await state.set_state(BroadcastStates.confirm)
    await message.answer("Начать рассылку? (да/нет)")


@router.message(BroadcastStates.message, F.text)
async def broadcast_text(message: Message, state: FSMContext) -> None:
    """Рассылка: текст."""
    await state.update_data(content_type="text", text=message.text)
    await state.set_state(BroadcastStates.confirm)
    await message.answer("Начать рассылку? (да/нет)")


@router.message(BroadcastStates.confirm, F.text)
async def broadcast_confirm(message: Message, state: FSMContext) -> None:
    """Подтверждение рассылки."""
    if message.text.strip().lower() not in ("да", "yes", "y"):
        await state.clear()
        await message.answer("Рассылка отменена.", reply_markup=get_main_keyboard())
        return

    data = await state.get_data()
    async with async_session_maker() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = [r[0] for r in result.fetchall()]

    bot = message.bot
    success = 0
    for uid in user_ids:
        try:
            if data.get("content_type") == "photo":
                await bot.send_photo(uid, data["file_id"], caption=data.get("caption", ""))
            elif data.get("content_type") == "video":
                await bot.send_video(uid, data["file_id"], caption=data.get("caption", ""))
            else:
                await bot.send_message(uid, data.get("text", ""))
            success += 1
        except Exception:
            pass
        await asyncio.sleep(0.05)

    await state.clear()
    await message.answer(f"Рассылка завершена. Доставлено: {success}/{len(user_ids)}", reply_markup=get_main_keyboard())


# ---------- Выгрузка в Google Sheets ----------
@router.callback_query(F.data == "admin:export")
async def admin_export(callback: CallbackQuery) -> None:
    """Выгрузка БД в Google Sheets."""
    if not is_superadmin(callback.from_user.id):
        await callback.answer("Доступ запрещён.", show_alert=True)
        return

    from config import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID
    creds_path = Path(GOOGLE_CREDENTIALS_PATH)

    if not creds_path.exists():
        await callback.message.edit_text(
            "Файл google_credentials.json не найден.\n"
            "Создайте сервисный аккаунт в Google Cloud и поместите JSON-ключ в корень проекта.",
            reply_markup=get_back_to_admin_keyboard(),
        )
        await callback.answer()
        return

    if not GOOGLE_SHEET_ID:
        await callback.message.edit_text(
            "GOOGLE_SHEET_ID не задан в .env.",
            reply_markup=get_back_to_admin_keyboard(),
        )
        await callback.answer()
        return

    await callback.answer("Выгрузка начата...")
    try:
        import gspread

        gc = gspread.service_account(filename=str(creds_path))
        sh = gc.open_by_key(GOOGLE_SHEET_ID)
        ws = sh.sheet1

        async with async_session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

        headers = ["id", "telegram_id", "role", "name", "phone", "driving_experience",
                   "motorcycle_type", "engine_capacity", "category_a", "city", "created_at"]
        rows = [headers]
        for u in users:
            rows.append([
                str(u.id), str(u.telegram_id), u.role or "", u.name or "", u.phone or "",
                str(u.driving_experience or ""), u.motorcycle_type or "", str(u.engine_capacity or ""),
                "Да" if u.category_a else "Нет", u.city or "", str(u.created_at) if u.created_at else "",
            ])

        ws.clear()
        if rows:
            ws.update("A1", rows)

        url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"
        await callback.message.answer(f"Выгрузка завершена.\n{url}", reply_markup=get_main_keyboard())
    except Exception as e:
        await callback.message.answer(f"Ошибка выгрузки: {e}", reply_markup=get_main_keyboard())
