from aiogram.fsm.state import State, StatesGroup


class ReminderStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_text = State()
    waiting_for_time = State()
    