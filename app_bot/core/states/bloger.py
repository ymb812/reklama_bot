from aiogram.fsm.state import State, StatesGroup


class BlogerStateGroup(StatesGroup):
    menu = State()
    stats = State()
    stats_update = State()
    reklams_list = State()
    paid_reklam_menu = State()
    send_content = State()
    ask_support = State()

    handle_answer_from_buyer = State()  # useless
