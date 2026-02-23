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
    ])


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка «Поделиться геопозицией»."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Поделиться геопозицией", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_skip_description_keyboard() -> InlineKeyboardMarkup:
    """Пропустить описание."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="sos_skip_desc")],
    ])


def get_help_button_keyboard(sos_id: int) -> InlineKeyboardMarkup:
    """Кнопка «Еду на помощь» под SOS-сообщением."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Еду на помощь", callback_data=f"sos_help:{sos_id}")],
    ])
