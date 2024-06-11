from aiogram.fsm.state import State, StatesGroup


class ManagerStateGroup(StatesGroup):
    menu = State()
    users_list = State()
    reklams_list = State()
    create_bloger_link = State()
    user_menu = State()
    input_price = State()
    send_task = State()
    ask_stats = State()
    handle_support = State()
    input_period = State()
    stats_by_period = State()

