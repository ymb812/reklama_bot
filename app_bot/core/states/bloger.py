from aiogram.fsm.state import State, StatesGroup


class BlogerStateGroup(StatesGroup):
    menu = State()
    stats = State()
    reklams_list = State()
    paid_reklam_menu = State()
    send_content = State()
