from aiogram.fsm.state import State, StatesGroup


class BlogerStateGroup(StatesGroup):
    menu = State()
    stats = State()
    reklams = State()
    reklam_menu = State()
