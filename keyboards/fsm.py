"""Клавиатуры навигации в FSM: Отмена и Назад."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Только кнопка «Отмена» (для первого шага FSM)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def get_back_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Кнопки «Назад» и «Отмена» (для шагов 2+ в FSM)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )
