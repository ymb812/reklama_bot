from aiogram.fsm.state import State, StatesGroup


class BuyerStateGroup(StatesGroup):
    menu = State()
    reklams = State()
    reklam_menu = State()
    stats = State()
