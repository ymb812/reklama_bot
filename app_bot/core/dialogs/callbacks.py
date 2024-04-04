import string
import random
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.common import ManagedScroll
from core.dialogs.custom_content import get_dialog_data
from core.states.agency import AgencyStateGroup
from core.states.manager import ManagerStateGroup
from core.states.buyer import BuyerStateGroup
from core.states.bloger import BlogerStateGroup
from core.database.models import User, Advertisement, StatusType
from core.utils.texts import _
from settings import settings


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def switch_page(dialog_manager: DialogManager, scroll_id: str):
    # switch page
    scroll: ManagedScroll = dialog_manager.find(scroll_id)
    current_page = await scroll.get_page()
    if current_page == dialog_manager.dialog_data['pages'] - 1:
        next_page = 0
    else:
        next_page = current_page + 1
    await scroll.set_page(next_page)


class AgencyManagerCallbackHandler:
    @staticmethod
    async def add_user(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        # handle manager states
        if 'manager_add_bloger' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
            await dialog_manager.switch_to(ManagerStateGroup.create_bloger_link)

        # handle agency states
        elif 'add_bloger' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
            dialog_manager.dialog_data['is_agency'] = True
            await dialog_manager.start(state=ManagerStateGroup.create_bloger_link, data=dialog_manager.dialog_data)

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
        if 'manager_blogers_list' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
            await dialog_manager.switch_to(ManagerStateGroup.users_list)

        # handle agency states
        elif 'blogers_list' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
            dialog_manager.dialog_data['is_agency'] = True
            await dialog_manager.start(state=ManagerStateGroup.users_list, data=dialog_manager.dialog_data)

        elif 'managers_list' in callback.data:
            dialog_manager.dialog_data['type'] = 'manager'
            dialog_manager.dialog_data['is_agency'] = True
            await dialog_manager.switch_to(AgencyStateGroup.users_list)


    @staticmethod
    async def entered_username(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        status = get_dialog_data(dialog_manager=dialog_manager, key='type')
        # create invite link
        link = settings.bot_link + generate_random_string(8)

        # handle tg_inst input
        text = value.split(' ')
        tg_username = text[0]
        inst_username = None

        # add inst_username
        if len(text) == 2:
            tg_username = text[0]
            inst_username = text[1]
        elif len(text) > 2:
            await message.answer(text=_('WRONG_USERNAME_INPUT'))
            return

        # add new user and send link
        agency_id = None
        manager = await User.get(user_id=message.from_user.id)
        if manager.status == StatusType.agency:  # check is manager agency
            agency_id = manager.id

        user = await User.create(
            username=tg_username,
            inst_username=inst_username,
            link=link,
            status=status,
            agency_id=agency_id,
            manager_id=manager.id
        )

        await message.answer(
            text=_(f'Пользователь со статусом {status} добавлен')
        )
        await message.answer(link)

        # handle new buyer
        if status == 'buyer':
            await Advertisement.filter(id=dialog_manager.dialog_data['current_reklam_id']).update(
                is_paid=True,
                buyer_id=user.id,
            )
            await dialog_manager.switch_to(ManagerStateGroup.reklams_list)


    @staticmethod
    async def selected_user(
            callback: CallbackQuery,
            widget: Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):
        dialog_manager.dialog_data['user_id'] = item_id
        if get_dialog_data(dialog_manager=dialog_manager, key='type') == 'bloger':
            await dialog_manager.switch_to(ManagerStateGroup.user_menu)  # 'bloger' could be only from Manager
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
        agency_id = None
        manager = await User.get(user_id=message.from_user.id)
        if manager.status == StatusType.agency:  # check is manager agency
            agency_id = manager.id

        bloger_id = dialog_manager.dialog_data['user_id']
        text = message.text
        if not message.text:
            text = message.caption

        adv = await Advertisement.create(
            text=text,
            photo_file_id=photo_file_id,
            video_file_id=video_file_id,
            document_file_id=document_file_id,
            agency_id=agency_id,
            manager_id=manager.id,
            bloger_id=bloger_id
        )
        await message.answer(text=_('TZ_IS_SENT'))

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


    @staticmethod
    async def list_of_reklams(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        dialog_manager.dialog_data['data_for_manager'] = True

        reklams = await Advertisement.filter(manager__user_id=dialog_manager.event.from_user.id).all()
        if not reklams:
            await callback.message.answer(text=_('THERE_IS_NO_REKLAMS'))
            return

        await dialog_manager.switch_to(ManagerStateGroup.reklams_list)


    @staticmethod
    async def list_of_reklams_for_agency(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        dialog_manager.dialog_data['data_for_manager'] = True
        dialog_manager.dialog_data['is_agency'] = True

        # reklams created by agency
        if widget.widget_id == 'agency_reklams_list':
            # just check to handle ValueError
            reklams = await Advertisement.filter(agency__user_id=dialog_manager.event.from_user.id).all()
            if not reklams:
                await callback.message.answer(text=_('THERE_IS_NO_REKLAMS'))
                return

        # reklams by agency's manager
        elif widget.widget_id == 'agency_manager_reklams':
            # save agency's picked manager to check his reklams
            manager_id = get_dialog_data(dialog_manager=dialog_manager, key='user_id')

            reklams = await Advertisement.filter(manager_id=manager_id).all()
            if not reklams:
                await callback.message.answer(text=_('THERE_IS_NO_REKLAMS'))
                return

            dialog_manager.dialog_data['manager_by_agency_id'] = manager_id

        await dialog_manager.start(state=ManagerStateGroup.reklams_list, data=dialog_manager.dialog_data)


    @staticmethod
    async def list_of_reklams_for_buyer(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        reklams = await Advertisement.filter(buyer__user_id=dialog_manager.event.from_user.id).all()
        if not reklams:
            await callback.message.answer(text=_('THERE_IS_NO_REKLAMS'))
            return

        dialog_manager.dialog_data['data_for_buyer'] = True
        await dialog_manager.switch_to(BuyerStateGroup.reklams_list)


    @staticmethod
    async def add_buyer(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        dialog_manager.dialog_data['type'] = 'buyer'
        await dialog_manager.switch_to(ManagerStateGroup.create_bloger_link)


class BlogerCallbackHandler:
    @staticmethod
    async def reklams_list(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        if widget.widget_id == 'reklams_approve':
            dialog_manager.dialog_data['is_paid'] = False
        elif widget.widget_id == 'paid_reklams':
            dialog_manager.dialog_data['is_paid'] = True

        # check is there any reklams
        if dialog_manager.dialog_data.get('is_paid'):
            reklams = await Advertisement.filter(
                bloger__user_id=dialog_manager.event.from_user.id, is_paid=True,
            ).all()
        else:
            reklams = await Advertisement.filter(
                bloger__user_id=dialog_manager.event.from_user.id, is_approved_by_bloger=False, is_rejected=False,
            ).all()

        if not reklams:
            await callback.message.answer(text=_('THERE_IS_NO_REKLAMS'))
            return

        await dialog_manager.switch_to(BlogerStateGroup.reklams_list)


    @staticmethod
    async def approve_or_reject_reklam(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        adv = await Advertisement.get_or_none(id=dialog_manager.dialog_data['current_reklam_id'])
        if widget.widget_id == 'approve_reklam':
            # change adv status and send msg to manager
            adv.is_approved_by_bloger = True

            await callback.message.answer(text='Далее как-то происходит согласование')

        elif widget.widget_id == 'reject_reklam':
            adv.is_rejected = True

        await switch_page(dialog_manager=dialog_manager, scroll_id='reklam_scroll')
        await adv.save()

        # last page
        if dialog_manager.dialog_data['pages'] == 1:
            await dialog_manager.switch_to(BlogerStateGroup.menu)
