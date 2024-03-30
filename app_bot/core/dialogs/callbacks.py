import string
import random
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from core.states.agency import AgencyStateGroup
from core.states.manager import ManagerStateGroup
from core.database.models import User, Advertisement, Dispatcher, Post
from core.keyboards.inline import handle_new_task_kb
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
        # handle manager states
        if 'manager_add_bloger' in callback.data:   # TODO: !!!!!!!!!!!!!!!
            dialog_manager.dialog_data['type'] = 'bloger'
            await dialog_manager.switch_to(ManagerStateGroup.create_bloger_link)
            return

        # handle agency states
        if 'add_bloger' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
        elif 'add_manager' in callback.data:
            dialog_manager.dialog_data['type'] = 'manager'

        await dialog_manager.switch_to(AgencyStateGroup.create_link)


    @staticmethod
    async def list_of_users(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        # handle manager states
        if 'manager_blogers_list' in callback.data:  # TODO: !!!!!!!!!!!!!!!
            dialog_manager.dialog_data['type'] = 'bloger'
            await dialog_manager.switch_to(ManagerStateGroup.users_list)
            return

        # handle agency states
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

        # handle tg_inst input
        text = value.split(' ')
        if len(text) == 2:
            tg_username = text[0]
            inst_username = text[1]

            dialog_manager.dialog_data['type'] = 'bloger'
            await User.create(
                username=tg_username,
                inst_username=inst_username,
                link=link,
                status=dialog_manager.dialog_data['type'],
            )

        # handle tgusername
        elif len(text) == 1:
            await User.create(
                username=value.strip(),
                link=link,
                status=dialog_manager.dialog_data['type'],
            )
        else:
            await message.answer(text=_('WRONG_USERNAME_INPUT'))
            return

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
        if dialog_manager.dialog_data['type'] == 'bloger':
            if widget.widget_id == '_bloger_select':  # TODO: !!!!!!!!!!!!!!!
                await dialog_manager.switch_to(ManagerStateGroup.user_menu)
            else:
                await dialog_manager.switch_to(AgencyStateGroup.user_menu)
        else:
            await dialog_manager.switch_to(AgencyStateGroup.user_menu)


    @staticmethod
    async def entered_task(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        # handle file input
        video_file_id, photo_file_id, document_file_id = None, None, None
        if message.video:
            video_file_id = message.video.file_id
        elif message.photo:
            photo_file_id = message.photo[-1].file_id
        elif message.document:
            document_file_id = message.document.file_id

        # save new adv
        manager = await User.get(user_id=message.from_user.id)
        bloger_id = dialog_manager.dialog_data['user_id']
        text = message.text
        if not message.text:
            text = message.caption

        adv = await Advertisement.create(
            text=text,
            photo_file_id=photo_file_id,
            video_file_id=video_file_id,
            document_file_id=document_file_id,
            manager_id=manager.id,
            bloger_id=bloger_id
        )

        # send task to the bloger
        bloger = await User.get_or_none(id=bloger_id)
        if bloger.user_id:
            await dialog_manager.event.bot.send_message(
                chat_id=bloger.user_id,
                text=f'Новое ТЗ от менеджера @{message.from_user.username}',
                reply_markup=handle_new_task_kb(adv_id=adv.id)
            )
            await message.forward(chat_id=bloger.user_id)
        else:
            await message.answer('Блогер еще не зарегистрировался в боте')

        await dialog_manager.switch_to(ManagerStateGroup.user_menu)


    @staticmethod
    async def ask_stats_from_user(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        await callback.message.answer('Здесь будет запрос статистики у блогера')

        await dialog_manager.switch_to(ManagerStateGroup.user_menu)


    @staticmethod
    async def check_stats(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        await callback.message.answer('Здесь будет просмотр статистики')

        await dialog_manager.switch_to(ManagerStateGroup.user_menu)
