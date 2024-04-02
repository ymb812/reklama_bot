from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.texts import _
from settings import settings


def mailing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('MAILING_BUTTON'), callback_data='start_mailing')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def payment_kb(agency_url: str, manager_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('AGENCY_PAY_BUTTON'), url=agency_url)
    kb.button(text=_('MANAGER_PAY_BUTTON'), url=manager_url)
    kb.button(text=_('SUPPORT_BUTTON'), url=settings.admin_chat_link)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def handle_new_task_kb(adv_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('CONFIRM_BUTTON'), callback_data=f'confirm_{adv_id}')  # handle
    kb.button(text=_('REJECT_BUTTON'), callback_data=f'reject_{adv_id}')  # do nothing
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
