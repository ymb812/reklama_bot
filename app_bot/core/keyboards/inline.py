from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.texts import _
from settings import settings


def mailing_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('MANAGER_MAILING_BUTTON'), callback_data='start_manager_mailing')
    kb.button(text=_('BLOGER_MAILING_BUTTON'), callback_data='start_bloger_mailing')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def payment_kb(agency_url: str, manager_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('AGENCY_PAY_BUTTON'), url=agency_url)
    kb.button(text=_('MANAGER_PAY_BUTTON'), url=manager_url)
    kb.button(text=_('SUPPORT_BUTTON'), url=settings.admin_chat_link)
    kb.button(text=_('Пробный период | Менеджер'), callback_data='freesubmanager')
    kb.button(text=_('Пробный период | Агентство'), callback_data='freesubagency')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def handle_paid_reklam_kb(adv_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('APPROVE_BUTTON'), callback_data=f'buyer_confirm_{adv_id}')
    kb.button(text=_('REQUEST_CHANGES_BUTTON'), callback_data=f'_buyer_reject_{adv_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def support_kb(adv_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('ANSWER_BUTTON'), callback_data=f'answer_{adv_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# save here user_id of msg sender and adv_id: '..._-4512322311_31'
def buyer_bloger_chat_kb(sender_user_id: str | int, adv_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Ответить', callback_data=f'send_msg_to_{sender_user_id}_{adv_id}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
