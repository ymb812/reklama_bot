from aiogram.fsm.state import State, StatesGroup


class BuyerStateGroup(StatesGroup):
    menu = State()
    reklams_list = State()
    send_msg_to_bloger = State()
    handle_reklam_from_bloger = State()

    handle_answer_from_bloger = State()  # useless
