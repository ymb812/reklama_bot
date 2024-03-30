from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.kbd import Button, SwitchTo, RequestContact, Select
from aiogram_dialog.widgets.input import TextInput, MessageInput
from core.dialogs.getters import get_input_data, get_users, get_user
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import AgencyManagerCallbackHandler
from core.states.agency import AgencyStateGroup
from core.utils.texts import _
from settings import settings


agency_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('ADD_BLOGER')), id='add_bloger', on_click=AgencyManagerCallbackHandler.add_user),
        Button(Const(text=_('ADD_MANAGER')), id='add_manager', on_click=AgencyManagerCallbackHandler.add_user),
        Button(Const(text=_('BLOGERS_LIST')), id='blogers_list', on_click=AgencyManagerCallbackHandler.list_of_users),
        Button(Const(text=_('MANAGERS_LIST')), id='managers_list', on_click=AgencyManagerCallbackHandler.list_of_users),
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
        Format(text=('Здесь какие-то кнопки для взаимодействия с пользователем {user.username}')),
        #Button(Const(text=_('DELETE')), id='delete_user', on_click=AgencyManagerCallbackHandler.add_user),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_list', state=AgencyStateGroup.users_list),
        getter=get_user,
        state=AgencyStateGroup.user_menu,
    ),
)
