import string
import random
from datetime import datetime
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.common import ManagedScroll
from core.dialogs.custom_content import get_dialog_data
from core.states.agency import AgencyStateGroup
from core.states.manager import ManagerStateGroup
from core.states.buyer import BuyerStateGroup
from core.states.bloger import BlogerStateGroup
from core.database.models import User, Advertisement, StatusType, UserStats
from core.keyboards.inline import handle_paid_reklam_kb, support_kb
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


def get_username_or_link(user: User):
    if user.username:
        user_username = f'@{user.username}'
    else:
        user_username = f'<a href="tg://user?id={user.user_id}">ссылка</a>'

    return user_username


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

        elif 'full_blogers_list' in callback.data:
            dialog_manager.dialog_data['type'] = 'bloger'
            dialog_manager.dialog_data['is_full_blogers_list'] = True
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
        manager = await User.get(user_id=message.from_user.id)
        agency_id = manager.agency_id  # if manager has agency, add bloger to the agency
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

        await message.answer(text=_('USER_IS_ADDED', status=status))
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
    async def entered_price(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: int | float,
    ):
        dialog_manager.dialog_data['price'] = value
        await dialog_manager.switch_to(ManagerStateGroup.send_task)


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
            price=dialog_manager.dialog_data['price'],
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
        # send request to the bloger
        manager = await User.get(user_id=callback.from_user.id)
        manager_username = get_username_or_link(user=manager)

        bloger_id = get_dialog_data(dialog_manager=dialog_manager, key='user_id')
        bloger = await User.get(id=bloger_id)
        bloger_username = get_username_or_link(user=bloger)

        if bloger.user_id:
            await dialog_manager.event.bot.send_message(
                chat_id=bloger.user_id,
                text=_('STATS_REQUEST', manager_username=manager_username)
            )
            await callback.message.answer(text=_('STATS_REQUEST_IS_SENT', bloger_username=bloger_username))

        # buyer has no user_id
        else:
            await callback.message.answer(text=_('USER_NOTIFICATION_ERROR'))
            return


        await dialog_manager.switch_to(ManagerStateGroup.user_menu)


    @staticmethod
    async def check_stats(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
            item_id: str | None = None,
    ):
        user_stats = await UserStats.get_or_none(user_id=get_dialog_data(dialog_manager=dialog_manager, key='user_id'))
        if not user_stats or not user_stats.video_file_id and not user_stats.document_file_id:
            await callback.message.answer(text='Блогер не загрузил статистику')
        else:
            # send video or document
            if user_stats.video_file_id:
                await callback.message.answer_video(video=user_stats.video_file_id)
            elif user_stats.document_file_id:
                await callback.message.answer_document(document=user_stats.document_file_id)

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
    async def edit_manager_percent(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: int | float,
    ):
        await User.filter(id=get_dialog_data(dialog_manager=dialog_manager, key='user_id')).update(
            manager_percent=value,
        )
        await dialog_manager.switch_to(state=AgencyStateGroup.user_menu)


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


    @staticmethod
    async def input_period(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        try:
            start_date_str, end_date_str = value.split('-')

            # check is data correct
            start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
            end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
        except ValueError:
            return

        dialog_manager.dialog_data['start_date_str'] = start_date_str
        dialog_manager.dialog_data['end_date_str'] = end_date_str
        await dialog_manager.switch_to(AgencyStateGroup.stats_by_period)


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

        elif widget.widget_id == 'reject_reklam':
            adv.is_rejected = True

        await switch_page(dialog_manager=dialog_manager, scroll_id='reklam_scroll')
        await adv.save()

        # last page
        if dialog_manager.dialog_data['pages'] == 1:
            await dialog_manager.switch_to(BlogerStateGroup.menu)


    @staticmethod
    async def reschedule_or_start_reklam(
            callback: CallbackQuery,
            widget: Button | Select,
            dialog_manager: DialogManager,
    ):
        adv = await Advertisement.get_or_none(id=dialog_manager.dialog_data['current_reklam_id'])
        buyer_user_id = (await adv.buyer).user_id
        dialog_manager.dialog_data['buyer_user_id'] = buyer_user_id

        # send info to buyer
        if widget.widget_id == 'start_reklam':
            if buyer_user_id:
                try:
                    await dialog_manager.event.bot.send_message(
                        chat_id=buyer_user_id,
                        text=_('BUYER_NOTIFICATION', reklam_id=adv.id)
                    )
                except:
                    await callback.message.answer(text=_('USER_NOTIFICATION_ERROR'))
                    return

                await callback.message.answer(text=_('BUYER_NOTIFICATION_IS_SENT'))

            # buyer has no user_id
            else:
                await callback.message.answer(text=_('USER_NOTIFICATION_ERROR'))
                return

            # going to get TZ
            await dialog_manager.switch_to(BlogerStateGroup.paid_reklam_menu)


        # create topic (if not exists) with manager and agent (if exists)
        elif widget.widget_id == 'reschedule_reklam':
            await dialog_manager.switch_to(BlogerStateGroup.ask_support)
            return


    @staticmethod
    async def entered_content(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        # send content to the buyer
        await message.copy_to(chat_id=dialog_manager.dialog_data['buyer_user_id'])
        await dialog_manager.event.bot.send_message(
            chat_id=dialog_manager.dialog_data['buyer_user_id'],
            text=_('PICK_ACTION_FOR_REKLAM', reklam_id=dialog_manager.dialog_data['current_reklam_id']),
            reply_markup=handle_paid_reklam_kb(adv_id=dialog_manager.dialog_data['current_reklam_id']),
        )

        await dialog_manager.switch_to(BlogerStateGroup.reklams_list)


    @staticmethod
    async def entered_stats(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        # handle file input
        video_file_id, document_file_id = None, None
        if message.video:
            video_file_id = message.video.file_id
        elif message.document:
            document_file_id = message.document.file_id

        # save video or document
        bloger = await User.get_or_none(user_id=message.from_user.id)
        user_stats = await UserStats.get_or_none(user=bloger)
        if not user_stats:
            await UserStats.create(user=bloger, video_file_id=video_file_id, document_file_id=document_file_id)
        else:
            user_stats.video_file_id = video_file_id
            user_stats.document_file_id = document_file_id
            await user_stats.save()

        await message.answer('Статистика успешно сохранена')
        await dialog_manager.switch_to(BlogerStateGroup.stats)


    @staticmethod
    async def entered_support_msg(
            message: Message,
            widget: MessageInput,
            dialog_manager: DialogManager,
    ):
        adv = await Advertisement.get_or_none(id=dialog_manager.dialog_data['current_reklam_id'])
        manager: User = await adv.manager

        # send support_request to the manager
        await message.copy_to(chat_id=manager.user_id)
        await dialog_manager.event.bot.send_message(
            chat_id=manager.user_id,
            text=_('BLOGER_REQUEST_SUPPORT', reklam_id=adv.id),
            reply_markup=support_kb(adv_id=dialog_manager.dialog_data['current_reklam_id']),
        )

        await message.answer(text=_('Сообщение отправлено, ожидайте ответа...'))
        await dialog_manager.switch_to(BlogerStateGroup.menu)
