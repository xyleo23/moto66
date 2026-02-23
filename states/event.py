"""FSM для создания мероприятия."""
from aiogram.fsm.state import State, StatesGroup


class EventCreationStates(StatesGroup):
    """Состояния создания мероприятия."""

    name = State()
    description = State()
    date_place = State()
    route = State()
    price = State()
    max_participants = State()
    min_experience = State()
    moto_type = State()
    min_engine_capacity = State()
