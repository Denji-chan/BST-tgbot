"""FSM holatlari."""
from aiogram.fsm.state import State, StatesGroup


class Reg(StatesGroup):
    lang = State()
    source = State()
    phone = State()
    name = State()


class EditName(StatesGroup):
    name = State()


class Broadcast(StatesGroup):
    content = State()
    confirm = State()


class Cashback(StatesGroup):
    find = State()      # mijozni topish
    amount = State()    # summa kiritish
    confirm = State()   # tasdiqlash


class FindCustomer(StatesGroup):
    query = State()


class SetPercent(StatesGroup):
    value = State()


class AddAdmin(StatesGroup):
    tg_id = State()
