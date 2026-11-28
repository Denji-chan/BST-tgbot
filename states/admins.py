from aiogram.fsm.state import State, StatesGroup


class AdminManage(StatesGroup):
    waiting_id = State()
