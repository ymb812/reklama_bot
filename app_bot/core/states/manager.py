from aiogram.fsm.state import State, StatesGroup


class ManagerStateGroup(StatesGroup):
    create_bloger_link = State()
    reklams = State()
    reklam_menu = State()
