"""Главное меню (Reply-клавиатура)."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard(show_admin: bool = False) -> ReplyKeyboardMarkup:
    """Reply-клавиатура главного меню. show_admin=True для СуперАдмина."""
    rows = [
        [KeyboardButton(text="Мероприятия")],
        [KeyboardButton(text="Заявка на двойку")],
        [KeyboardButton(text="Кнопка SOS 🆘")],
        [KeyboardButton(text="Мой профиль")],
    ]
    if show_admin:
        rows.append([KeyboardButton(text="👑 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
