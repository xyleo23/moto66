"""FSM для заявки на двойку."""
from aiogram.fsm.state import State, StatesGroup


class DoubleRequestStates(StatesGroup):
    """Состояния заявки на двойку."""

    date_route = State()
