from aiogram.fsm.state import State, StatesGroup


class PurchaseEntry(StatesGroup):
    customer = State()
    items = State()
    cashback = State()
    confirm = State()
