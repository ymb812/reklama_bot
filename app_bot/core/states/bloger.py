from aiogram.fsm.state import State, StatesGroup


class BlogerStateGroup(StatesGroup):
    menu = State()
    stats = State()
    reklams_list = State()
    reklam_menu = State()
