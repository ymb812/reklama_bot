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
from core.states.buyer import BuyerStateGroup
from core.utils.texts import _
from settings import settings


buyer_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Button(Const(text=_('REKLAMS_LIST')), id='reklams_list', on_click=AgencyManagerCallbackHandler.list_of_reklams_for_buyer),
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
            # # add buyer
            # Button(
            #     Const(text=_('ADD_BUYER_BUTTON')),
            #     id='add_buyer',
            #     on_click=AgencyManagerCallbackHandler.add_buyer,
            #     when=F['is_paid'] == False,
            # ),

            SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=BuyerStateGroup.menu),
        ),

        getter=get_reklams_by_status,
        state=BuyerStateGroup.reklams_list,
    ),
)
