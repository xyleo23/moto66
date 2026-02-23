"""FSM для рассылки."""
from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """Состояния рассылки."""

    message = State()
    confirm = State()
