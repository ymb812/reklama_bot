from aiogram import F
from aiogram.types import ContentType
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
        SwitchTo(Const(text=_('STATS_BUTTON')), id='get_stats', state=BlogerStateGroup.stats),
        Button(Const(text=_('REKLAMS_APPROVE_BUTTON')), id='reklams_approve', on_click=BlogerCallbackHandler.reklams_list),
        Button(Const(text=_('PAID_REKLAMS_BUTTON')), id='paid_reklams', on_click=BlogerCallbackHandler.reklams_list),
        state=BlogerStateGroup.menu,
    ),

    # stats
    Window(
        Const(text=_('Какие-то действия со статистикой')),
        Button(Const(text=_('UPDATE_STATS_BUTTON')), id='update_stats'),
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

            # buttons for paid_reklams
            Button(
                Const(text=_('START_TZ_BUTTON')),
                id='start_reklam',
                on_click=BlogerCallbackHandler.reschedule_or_start_reklam,
                when=F.get('dialog_data').get('is_paid') == True,
            ),
            Button(
                Const(text=_('RESCHEDULE_BUTTON')),
                id='reschedule_reklam',
                on_click=BlogerCallbackHandler.reschedule_or_start_reklam,
                when=F.get('dialog_data').get('is_paid') == True,
            ),

            SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=BlogerStateGroup.menu),
        ),

        getter=get_reklams_by_status,
        state=BlogerStateGroup.reklams_list,
    ),

    # paid reklam menu
    Window(
        Const(text=_('SEND_CONTENT')),
        SwitchTo(Const(text=_('SEND_CONTENT_BUTTON')), id='send_content', state=BlogerStateGroup.send_content),
        state=BlogerStateGroup.paid_reklam_menu,
    ),

    # task input
    Window(
        Const(text=_('SEND_CONTENT_TO_BUYER')),
        MessageInput(
            func=BlogerCallbackHandler.entered_content,
            content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT]
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_paid_menu', state=BlogerStateGroup.paid_reklam_menu),
        state=BlogerStateGroup.send_content
    ),
)
