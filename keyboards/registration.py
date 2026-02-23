"""Клавиатуры для регистрации и анкеты."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_contact_keyboard(has_back: bool = True) -> ReplyKeyboardMarkup:
    """Кнопка «Поделиться контактом» + навигация."""
    from keyboards.fsm import get_back_cancel_keyboard, get_cancel_keyboard
    nav = get_back_cancel_keyboard() if has_back else get_cancel_keyboard()
    rows = list(nav.keyboard) + [[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def get_moto_type_keyboard() -> InlineKeyboardMarkup:
    """Inline: тип мотоцикла."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Спорт", callback_data="moto:спорт"),
            InlineKeyboardButton(text="Турист", callback_data="moto:турист"),
        ],
        [
            InlineKeyboardButton(text="Круизер", callback_data="moto:круизер"),
            InlineKeyboardButton(text="Эндуро", callback_data="moto:эндуро"),
        ],
        [InlineKeyboardButton(text="Нейкед", callback_data="moto:нейкед")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
    ])


def get_category_a_keyboard() -> InlineKeyboardMarkup:
    """Inline: права категории А."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="cat_a:yes"),
            InlineKeyboardButton(text="Нет", callback_data="cat_a:no"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_fsm")],
    ])


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Inline: кнопка «Пропустить»."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip")]
    ])
