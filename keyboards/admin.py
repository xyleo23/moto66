"""Клавиатуры админ-панели."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать мероприятие", callback_data="admin:create_event")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="📢 Создать рассылку", callback_data="admin:broadcast")],
        [InlineKeyboardButton(text="📥 Выгрузить БД", callback_data="admin:export")],
    ])


def get_moto_type_event_keyboard() -> InlineKeyboardMarkup:
    """Тип мото для мероприятия (или любой)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Спорт", callback_data="emoto:спорт"),
            InlineKeyboardButton(text="Турист", callback_data="emoto:турист"),
        ],
        [
            InlineKeyboardButton(text="Круизер", callback_data="emoto:круизер"),
            InlineKeyboardButton(text="Эндуро", callback_data="emoto:эндуро"),
        ],
        [
            InlineKeyboardButton(text="Нейкед", callback_data="emoto:нейкед"),
            InlineKeyboardButton(text="Любой", callback_data="emoto:любой"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
    ])


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Кнопка «Назад в админку»."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:back")],
    ])
