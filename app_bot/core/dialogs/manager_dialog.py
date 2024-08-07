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
from core.dialogs.getters import get_users, get_user, get_reklams_by_status, get_manager_stats_by_period, get_manager
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
            when=F.get('start_data') == None,
        ),
        # manager from agency
        Start(
            Const(text=_('BACK_BUTTON')),
            id='go_to_agency',
            state=AgencyStateGroup.menu,
            when=F.get('start_data').get('is_agency') == True,
        ),
)


manager_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ADD_BLOGER_BUTTON')), id='manager_add_bloger', on_click=AgencyManagerCallbackHandler.add_user),
        Button(Const(text=_('BLOGERS_LIST_BUTTON')), id='manager_blogers_list', on_click=AgencyManagerCallbackHandler.list_of_users),
        Button(Const(text=_('FULL_BLOGERS_LIST_BUTTON')), id='full_blogers_list', on_click=AgencyManagerCallbackHandler.list_of_users,
               when=F['user'].agency_id),
        Button(Const(text=_('REKLAMS_LIST_BUTTON')), id='reklams_list', on_click=AgencyManagerCallbackHandler.list_of_reklams),
        SwitchTo(Const(text='Заработок за период'), id='manager_income', state=ManagerStateGroup.input_period,
                 when=~F['user'].agency_id),
        getter=get_manager,
        state=ManagerStateGroup.menu,
    ),

    # username input
    Window(
        Const(text=_('INPUT_USERNAME_AND_INST'), when=F.get('dialog_data').get('type') != 'buyer'),
        Const(text=_('INPUT_BUYER_USERNAME'), when=F.get('dialog_data').get('type') == 'buyer'),
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
        Format(text=_('PICK_BLOGER_ACTION', inst_username='{user.inst_username}')),
        SwitchTo(Const(text=_('SEND_TASK_BUTTON')), id='send_task', state=ManagerStateGroup.input_price),
        SwitchTo(Const(text=_('STATS_BUTTON')), id='ask_stats', state=ManagerStateGroup.ask_stats),
        # Button(Const(text=_('DELETE')), id='delete_user', on_click=AgencyManagerCallbackHandler.delete_user),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_list', state=ManagerStateGroup.users_list),
        getter=get_user,
        state=ManagerStateGroup.user_menu,
    ),

    # input_price
    Window(
        Const(text='Введите число - стоимость в рублях'),
        TextInput(
            id='input_price',
            type_factory=float,
            on_success=AgencyManagerCallbackHandler.entered_price,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_user_menu', state=ManagerStateGroup.user_menu),
        state=ManagerStateGroup.input_price,
    ),

    # task input
    Window(
        Const(text=_('INPUT_TASK')),
        MessageInput(
            func=AgencyManagerCallbackHandler.entered_task,
            content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_input_price', state=ManagerStateGroup.input_price),
        state=ManagerStateGroup.send_task,
    ),

    # stats request
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ASK_STATS_BUTTON')), id='ask_stats', on_click=AgencyManagerCallbackHandler.ask_stats_from_user),
        Button(Const(text=_('CHECK_STATS_BUTTON')), id='check_stats', on_click=AgencyManagerCallbackHandler.check_stats),
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
        ),
        specific_back_buttons,

        getter=get_reklams_by_status,
        state=ManagerStateGroup.reklams_list,
    ),

    # input_period
    Window(
        Const(text='Введите период в формате: <code>01.05.2024-11.05.2024</code>'),
        TextInput(
            id='input_period_manager',
            type_factory=str,
            on_success=AgencyManagerCallbackHandler.input_period
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=ManagerStateGroup.menu),
        state=ManagerStateGroup.input_period,
    ),

    # stats_by_period
    Window(
        Format(text='<b>Доход:</b> {full_income} рублей\n'
                    '<b>Кол-во ТЗ:</b> {advertisements_amount}\n'),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_input_period', state=ManagerStateGroup.input_period),
        getter=get_manager_stats_by_period,
        state=ManagerStateGroup.stats_by_period,
    ),
)
