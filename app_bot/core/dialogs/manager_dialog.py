from aiogram import F
from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.kbd import PrevPage, NextPage, CurrentPage, Start, Column, StubScroll, Button, Row, \
    FirstPage, LastPage, SwitchTo, Select
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import AgencyManagerCallbackHandler
from core.dialogs.getters import get_users, get_user, get_reklams_by_status
from core.states.manager import ManagerStateGroup
from core.states.agency import AgencyStateGroup
from core.utils.texts import _
from settings import settings


specific_back_buttons = Column(
        # manager from manager
        SwitchTo(
            Const(text=_('BACK_BUTTON')),
            id='go_to_manager',
            state=ManagerStateGroup.menu,
            when=F.get('start_data') == None and F.get('dialog_data').get('type') != 'buyer',
        ),
        # manager from agency
        Start(
            Const(text=_('BACK_BUTTON')),
            id='go_to_agency',
            state=AgencyStateGroup.menu,
            when=F.get('start_data').get('is_agency') == True and F.get('dialog_data').get('type') != 'buyer',
        ),
        # go back to the reklams list
        SwitchTo(
            Const(text=_('BACK_BUTTON')),
            id='go_to_reklams',
            state=ManagerStateGroup.reklams_list,
            when=F['dialog_data']['type'] == 'buyer',
        ),
)


manager_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ADD_BLOGER')), id='manager_add_bloger', on_click=AgencyManagerCallbackHandler.add_user),
        Button(Const(text=_('BLOGERS_LIST')), id='manager_blogers_list', on_click=AgencyManagerCallbackHandler.list_of_users),
        Button(Const(text=_('REKLAMS_LIST')), id='reklams_list', on_click=AgencyManagerCallbackHandler.list_of_reklams),
        state=ManagerStateGroup.menu,
    ),

    # username input
    Window(
        Const(text=_('INPUT_USERNAME_AND_INST'), when=F['dialog_data']['type'] != 'buyer'),
        Const(text=_('Введите ник заказчика, с которым согласовали рекламу'), when=F['dialog_data']['type'] == 'buyer'),
        TextInput(
            id='input_tg_inst',
            type_factory=str,
            on_success=AgencyManagerCallbackHandler.entered_username
        ),
        specific_back_buttons,
        state=ManagerStateGroup.create_bloger_link,
    ),

    Window(
        Const(text=_('PICK_USER')),
        CustomPager(
            Select(
                id='_bloger_select',
                items='users',
                item_id_getter=lambda item: item.id,
                text=Format(text='{item.inst_username}'),
                on_click=AgencyManagerCallbackHandler.selected_user,
            ),
            id='user_group',
            height=settings.categories_per_page_height,
            width=settings.categories_per_page_width,
            hide_on_single_page=True,
        ),
        specific_back_buttons,
        getter=get_users,
        state=ManagerStateGroup.users_list,
    ),

    # user menu
    Window(
        Format(text='Выберите действие с блогером {user.inst_username}'),
        SwitchTo(Const(text=_('SEND_TASK')), id='send_task', state=ManagerStateGroup.send_task),
        SwitchTo(Const(text=_('ASK_STATS')), id='ask_stats', state=ManagerStateGroup.ask_stats),
        # Button(Const(text=_('DELETE')), id='delete_user', on_click=AgencyManagerCallbackHandler.delete_user),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_list', state=ManagerStateGroup.users_list),
        getter=get_user,
        state=ManagerStateGroup.user_menu,
    ),

    # task input
    Window(
        Const(text=_('INPUT_TASK')),
        MessageInput(
            func=AgencyManagerCallbackHandler.entered_task,
            content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_user_menu', state=ManagerStateGroup.user_menu),
        state=ManagerStateGroup.send_task,
    ),

    # stats request
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ASK_STATS')), id='ask_stats', on_click=AgencyManagerCallbackHandler.ask_stats_from_user),
        Button(Const(text=_('CHECK_STATS')), id='check_stats', on_click=AgencyManagerCallbackHandler.check_stats),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_user_menu', state=ManagerStateGroup.user_menu),
        state=ManagerStateGroup.ask_stats,
    ),

    # reklams
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{data_for_manager}'),
        StubScroll(id='reklam_scroll', pages='pages'),

        # cycle pager
        Row(
            LastPage(scroll='reklam_scroll', text=Const('<'), when=F['current_page'] == 0),
            PrevPage(scroll='reklam_scroll', when=F['current_page'] != 0),
            CurrentPage(scroll='reklam_scroll'),
            NextPage(scroll='reklam_scroll', when=F['current_page'] != F['pages'] - 1),  # if last: go to the first page
            FirstPage(scroll='reklam_scroll', text=Const('>'), when=F['current_page'] == F['pages'] - 1),
            when=F['pages'] > 1,
        ),

        Column(
            # add buyer
            Button(
                Const(text=_('ADD_BUYER_BUTTON')),
                id='add_buyer',
                on_click=AgencyManagerCallbackHandler.add_buyer,
                when=F['is_paid'] == False,
            ),

            SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=ManagerStateGroup.menu),
        ),

        getter=get_reklams_by_status,
        state=ManagerStateGroup.reklams_list,
    ),
)
