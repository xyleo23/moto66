"""FSM для SOS-сигнала."""
from aiogram.fsm.state import State, StatesGroup


class SosStates(StatesGroup):
    """Состояния SOS."""

    problem_type = State()
    location = State()
    description = State()
