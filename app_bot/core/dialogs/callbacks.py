import string
import random
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from core.states.agency import AgencyStateGroup
from core.database.models import User, Dispatcher, Post
from core.utils.texts import _
from settings import settings


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class CallBackHandler:
    @staticmethod
    async def add_user(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        if 'add_bloger' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
        elif 'add_manager' in callback.data:
            dialog_manager.dialog_data['type'] = 'manager'
            pass

        await dialog_manager.switch_to(AgencyStateGroup.create_link)


    @staticmethod
    async def list_of_users(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        if 'blogers_list' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
        elif 'managers_list' in callback.data:
            dialog_manager.dialog_data['type'] = 'manager'

        await dialog_manager.switch_to(AgencyStateGroup.users_list)


    @staticmethod
    async def entered_username(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        # create invite link
        link = settings.bot_link + generate_random_string(8)
        await User.create(
            username=value.strip(),
            link=link,
            status=dialog_manager.dialog_data['type'],
        )

        await message.answer(text=_(f'Пользователь со статусом {dialog_manager.dialog_data["type"]} добавлен'))
        await message.answer(link)


    @staticmethod
    async def selected_user(
            callback: CallbackQuery,
            widget: Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):
        dialog_manager.dialog_data['user_id'] = item_id
        await dialog_manager.switch_to(AgencyStateGroup.user_menu)
