from aiogram.fsm.state import State, StatesGroup


class EditText(StatesGroup):
    waiting_text = State()
