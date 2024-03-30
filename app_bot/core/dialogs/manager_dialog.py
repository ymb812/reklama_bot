from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Select
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import AgencyManagerCallbackHandler
from core.dialogs.getters import get_users, get_user
from core.states.manager import ManagerStateGroup
from core.utils.texts import _
from settings import settings


manager_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ADD_BLOGER')), id='manager_add_bloger', on_click=AgencyManagerCallbackHandler.add_user),   # TODO: !!!!!!!!!!!!!!!
        Button(Const(text=_('BLOGERS_LIST')), id='manager_blogers_list', on_click=AgencyManagerCallbackHandler.list_of_users),   # TODO: !!!!!!!!!!!!!!!
        state=ManagerStateGroup.menu,
    ),

    # username input
    Window(
        Const(text=_('INPUT_USERNAME_AND_INST')),
        TextInput(
            id='input_tg_inst',
            type_factory=str,
            on_success=AgencyManagerCallbackHandler.entered_username
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=ManagerStateGroup.menu),
        state=ManagerStateGroup.create_bloger_link,
    ),

    Window(
        Const(text=_('PICK_USER')),
        CustomPager(
            Select(
                id='_bloger_select',  # TODO: !!!!!!!!!!!!!!!
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
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=ManagerStateGroup.menu),
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
)
