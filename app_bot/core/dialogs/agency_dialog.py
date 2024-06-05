from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.kbd import Button, SwitchTo, RequestContact, Select
from aiogram_dialog.widgets.input import TextInput, MessageInput
from core.dialogs.getters import get_users, get_user, get_stats_by_period
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import AgencyManagerCallbackHandler
from core.states.agency import AgencyStateGroup
from core.utils.texts import _
from settings import settings


agency_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ADD_BLOGER_BUTTON')), id='add_bloger',
               on_click=AgencyManagerCallbackHandler.add_user),
        Button(Const(text=_('ADD_MANAGER_BUTTON')), id='add_manager',
               on_click=AgencyManagerCallbackHandler.add_user),
        Button(Const(text=_('BLOGERS_LIST_BUTTON')), id='blogers_list',
               on_click=AgencyManagerCallbackHandler.list_of_users),
        Button(Const(text=_('MANAGERS_LIST_BUTTON')), id='managers_list',
               on_click=AgencyManagerCallbackHandler.list_of_users),
        Button(Const(text=_('REKLAMS_LIST_BUTTON')), id='agency_reklams_list',
               on_click=AgencyManagerCallbackHandler.list_of_reklams_for_agency),
        SwitchTo(Const(text='Заработок за период'), id='agency_income', state=AgencyStateGroup.input_period),

        state=AgencyStateGroup.menu,
    ),

    # username input
    Window(
        Const(text=_('INPUT_USERNAME')),
        TextInput(
            id='input_username',
            type_factory=str,
            on_success=AgencyManagerCallbackHandler.entered_username
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=AgencyStateGroup.menu),
        state=AgencyStateGroup.create_link,
    ),

    # users
    Window(
        Const(text=_('PICK_USER')),
        CustomPager(
            Select(
                id='_user_select',
                items='users',
                item_id_getter=lambda item: item.id,
                text=Format(text='{item.username}'),
                on_click=AgencyManagerCallbackHandler.selected_user,
            ),
            id='user_group',
            height=settings.categories_per_page_height,
            width=settings.categories_per_page_width,
            hide_on_single_page=True,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=AgencyStateGroup.menu),
        getter=get_users,
        state=AgencyStateGroup.users_list,
    ),

    # user menu
    Window(
        Format(text='<b>Текущий процент менеджера:</b> {user.manager_percent}%\n\n'
                    '<b>Сумма реклам:</b> {reklams_sum} рублей'),
        Button(
            Const(text=_('REKLAMS_LIST_BUTTON')),
            id='agency_manager_reklams',
            on_click=AgencyManagerCallbackHandler.list_of_reklams_for_agency
        ),
        #Button(Const(text=_('DELETE')), id='delete_user', on_click=AgencyManagerCallbackHandler.add_user),
        SwitchTo(Const(text='Изменить процент с продаж'), id='edit_manager_percent', state=AgencyStateGroup.edit_manager_percent),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_list', state=AgencyStateGroup.users_list),
        getter=get_user,
        state=AgencyStateGroup.user_menu,
    ),

    # edit_manager_percent
    Window(
        Format(text='Введите число\n\n<i>Текущий процент менеджера: {user.manager_percent}%</i>'),
        TextInput(
            id='input_manager_percent',
            type_factory=float,
            on_success=AgencyManagerCallbackHandler.edit_manager_percent,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_user_menu', state=AgencyStateGroup.user_menu),
        getter=get_user,
        state=AgencyStateGroup.edit_manager_percent,
    ),

    # input_period
    Window(
        Const(text='Введите период в формате: <code>01.05.2024-11.05.2024</code>'),
        TextInput(
            id='input_period_agency',
            type_factory=str,
            on_success=AgencyManagerCallbackHandler.input_period
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=AgencyStateGroup.menu),
        state=AgencyStateGroup.input_period,
    ),

    # stats_by_period
    Window(
        Format(text='<b>Доход:</b> {full_income} рублей\n'
                    '<b>Чистая прибыль :</b> {clear_income} рублей\n'
                    '<b>Процент сотрудникам:</b> {managers_income} рублей\n'
                    '<b>Кол-во ТЗ:</b> {advertisements_amount}\n'),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_input_period', state=AgencyStateGroup.input_period),
        getter=get_stats_by_period,
        state=AgencyStateGroup.stats_by_period,
    ),
)
