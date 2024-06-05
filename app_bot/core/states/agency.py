from aiogram.fsm.state import State, StatesGroup


class AgencyStateGroup(StatesGroup):
    menu = State()
    create_link = State()
    users_list = State()
    user_menu = State()
    edit_manager_percent = State()
