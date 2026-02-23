"""Обработчики /start и проверка регистрации."""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import SUPERADMIN_ID
from keyboards.main_menu import get_main_keyboard
from services.user import get_user_by_telegram_id
from states.registration import RegistrationStates
from handlers.registration import start_registration

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Проверка: есть ли пользователь в БД. Если нет — анкета."""
    await state.clear()

    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        role_note = " (Админ)" if message.from_user.id == SUPERADMIN_ID else ""
        show_admin = message.from_user.id == SUPERADMIN_ID
        await message.answer(
            f"С возвращением, {user.name or 'водитель'}!{role_note}\n\n"
            "Выберите действие:",
            reply_markup=get_main_keyboard(show_admin=show_admin),
        )
        return

    await message.answer(
        "👋 Добро пожаловать в закрытое мотосообщество!\n\n"
        "Чтобы получить доступ к мероприятиям и функциям бота, "
        "пожалуйста, пройди короткую регистрацию."
    )
    await start_registration(message, state)


@router.message(F.text == "/start")
async def cmd_start_text(message: Message, state: FSMContext) -> None:
    """Дубликат на текстовый /start."""
    await cmd_start(message, state)
