"""FSM для регистрации пользователя."""
from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния анкеты регистрации."""

    name = State()
    phone = State()
    driving_experience = State()
    motorcycle_type = State()
    engine_capacity = State()
    category_a = State()
    city = State()
