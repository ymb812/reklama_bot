from aiogram import F
from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.kbd import PrevPage, NextPage, CurrentPage, Start, Column, StubScroll, Button, Row, \
    FirstPage, LastPage, SwitchTo, Select
from core.dialogs.callbacks import AgencyManagerCallbackHandler, BuyerCallbackHandler
from core.dialogs.getters import get_users, get_user, get_reklams_by_status
from core.states.buyer import BuyerStateGroup
from core.utils.texts import _


buyer_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(
            Const(text=_('REKLAMS_LIST_BUTTON')),
            id='reklams_list',
            on_click=AgencyManagerCallbackHandler.list_of_reklams_for_buyer
        ),
        state=BuyerStateGroup.menu,
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
            SwitchTo(
                Const(text='Написать блогеру'),
                id='chat_with_bloger',
                state=BuyerStateGroup.send_msg_to_bloger,
            ),
            SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=BuyerStateGroup.menu),
        ),

        getter=get_reklams_by_status,
        state=BuyerStateGroup.reklams_list,
    ),

    # send_msg_to_bloger
    Window(
        Format(text=f'Введите сообщение - оно отправится блогеру'),
        MessageInput(
            func=BuyerCallbackHandler.entered_message_for_bloger,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_reklams_list', state=BuyerStateGroup.reklams_list),
        state=BuyerStateGroup.send_msg_to_bloger,
    ),
)
