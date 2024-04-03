from aiogram.fsm.state import State, StatesGroup


class ManagerStateGroup(StatesGroup):
    menu = State()
    users_list = State()
    reklams_list = State()
    create_bloger_link = State()
    user_menu = State()
    send_task = State()
    ask_stats = State()
