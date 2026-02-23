"""Глобальный хэндлер Отмены: /cancel, кнопка «❌ Отмена» и callback cancel_fsm."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import SUPERADMIN_ID
from keyboards.main_menu import get_main_keyboard
from services.user import get_user_by_telegram_id

router = Router(name="cancel")


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Очистить стейт и вернуть в главное меню."""
    await state.clear()
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        show_admin = message.from_user.id == SUPERADMIN_ID
        await message.answer("Действие отменено.", reply_markup=get_main_keyboard(show_admin=show_admin))
    else:
        await message.answer("Регистрация отменена. Нажмите /start для начала.")


@router.callback_query(F.data == "cancel_fsm")
async def callback_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена по inline-кнопке."""
    await state.clear()
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user:
        show_admin = callback.from_user.id == SUPERADMIN_ID
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Действие отменено.", reply_markup=get_main_keyboard(show_admin=show_admin))
    else:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Регистрация отменена. Нажмите /start для начала.")
    await callback.answer()
