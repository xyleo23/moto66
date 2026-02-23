"""Клавиатуры SOS."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def get_sos_problem_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа проблемы."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ДТП", callback_data="sos:ДТП"),
            InlineKeyboardButton(text="Закончился бензин", callback_data="sos:Закончился бензин"),
        ],
        [
            InlineKeyboardButton(text="Тех. поломка", callback_data="sos:Тех. поломка"),
            InlineKeyboardButton(text="Другое", callback_data="sos:Другое"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
    ])


def get_location_keyboard(has_back: bool = True) -> ReplyKeyboardMarkup:
    """Кнопка «Поделиться геопозицией» + навигация."""
    from keyboards.fsm import get_back_cancel_keyboard, get_cancel_keyboard
    nav = get_back_cancel_keyboard() if has_back else get_cancel_keyboard()
    rows = list(nav.keyboard) + [[KeyboardButton(text="📍 Поделиться геопозицией", request_location=True)]]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def get_skip_description_keyboard() -> InlineKeyboardMarkup:
    """Пропустить описание + навигация."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="sos_skip_desc")],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="sos_back:location"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm"),
        ],
    ])


def get_help_button_keyboard(sos_id: int) -> InlineKeyboardMarkup:
    """Кнопка «Еду на помощь» под SOS-сообщением."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Еду на помощь", callback_data=f"sos_help:{sos_id}")],
    ])
