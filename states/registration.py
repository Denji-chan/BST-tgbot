from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    language = State()
    first_name = State()
    last_name = State()
    phone = State()
    birth_date = State()
    confirm = State()
