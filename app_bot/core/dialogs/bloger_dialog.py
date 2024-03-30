from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.kbd import PrevPage, NextPage, CurrentPage, Start, Column, StubScroll, Button, Row, \
    FirstPage, LastPage, SwitchTo
from aiogram_dialog.widgets.input import TextInput, MessageInput
from core.dialogs.getters import get_input_data, get_users, get_user, get_reklams_by_status
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import BlogerCallbackHandler, AgencyManagerCallbackHandler
from core.states.bloger import BlogerStateGroup
from core.utils.texts import _
from settings import settings


bloger_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        SwitchTo(Const(text=_('MY_STATS')), id='get_stats', state=BlogerStateGroup.stats),
        Button(Const(text=_('REKLAMS_APPROVE')), id='reklams_approve', on_click=BlogerCallbackHandler.reklams_list),
        Button(Const(text=_('PAID_REKLAMS')), id='paid_reklams', on_click=BlogerCallbackHandler.reklams_list),
        state=BlogerStateGroup.menu,
    ),

    # stats
    Window(
        Const(text=_('Какие-то действия со статистикой')),
        Button(Const(text=_('UPDATE_STATS')), id='update_stats'),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=BlogerStateGroup.menu),
        state=BlogerStateGroup.stats,
    ),

    # reklams
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{description}'),
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
            # buttons for reklams_approve
            Button(
                Const(text=_('APPROVE_BUTTON')),
                id='approve_reklam',
                on_click=BlogerCallbackHandler.approve_or_reject_reklam,
                when=F.get('dialog_data').get('is_paid') != True,
            ),
            Button(
                Const(text=_('REJECT_BUTTON')),
                id='reject_reklam',
                on_click=BlogerCallbackHandler.approve_or_reject_reklam,
                when=F.get('dialog_data').get('is_paid') != True,
            ),
            # TODO: ADD BUTTONS FOR IS_PAID REKLAMS

            SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=BlogerStateGroup.menu),
        ),

        getter=get_reklams_by_status,
        state=BlogerStateGroup.reklams_list,
    ),
)
