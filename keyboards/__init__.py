"""Клавиатуры бота."""
from keyboards.main_menu import get_main_keyboard
from keyboards.registration import (
    get_moto_type_keyboard,
    get_category_a_keyboard,
    get_skip_keyboard,
)

__all__ = [
    "get_main_keyboard",
    "get_moto_type_keyboard",
    "get_category_a_keyboard",
    "get_skip_keyboard",
]
