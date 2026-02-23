"""Клавиатуры для регистрации и анкеты."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка «Поделиться контактом»."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


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
    ])


def get_category_a_keyboard() -> InlineKeyboardMarkup:
    """Inline: права категории А."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="cat_a:yes"),
            InlineKeyboardButton(text="Нет", callback_data="cat_a:no"),
        ],
    ])


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Inline: кнопка «Пропустить»."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip")]
    ])
