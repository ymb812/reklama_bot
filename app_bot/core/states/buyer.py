from aiogram.fsm.state import State, StatesGroup


class BuyerStateGroup(StatesGroup):
    menu = State()
    reklams_list = State()
    reklam_menu = State()
    stats = State()
    handle_reklam_from_bloger = State()
