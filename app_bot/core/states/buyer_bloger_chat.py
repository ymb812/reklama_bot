from aiogram.fsm.state import State, StatesGroup


class BuyerBlogerChatStateGroup(StatesGroup):
    handle_answer = State()
