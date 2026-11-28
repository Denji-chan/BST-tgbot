from aiogram.fsm.state import State, StatesGroup


class SupportRequest(StatesGroup):
    waiting_message = State()


class SupportReply(StatesGroup):
    waiting_answer = State()
