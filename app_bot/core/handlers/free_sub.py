import logging
import pytz
from datetime import datetime, timedelta
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode
from core.database.models import User
from core.states.free_sub import FreeSubStateGroup
from core.states.agency import AgencyStateGroup
from core.states.manager import ManagerStateGroup
from core.utils.texts import set_admin_commands, _
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Free sub router')


@router.callback_query(lambda c: 'freesubmanager' in c.data or 'freesubagency' in c.data)
async def handle_support_from_bloger(callback: types.CallbackQuery, bot: Bot, state: FSMContext, dialog_manager: DialogManager):
    # check is user new
    if await User.get_or_none(user_id=callback.from_user.id):
        await callback.message.answer(text=_('Пробная подписка доступна только новым пользователям'))
        return

    if callback.data == 'freesubmanager':
        status = 'manager'
    else:
        status = 'agency'

    # set status and give FREE sub days
    subscription_ends_at = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=settings.free_sub_days)
    await User.update_data(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        status=status,
        subscription_ends_at=subscription_ends_at,
    )
    await callback.message.answer(text=f'Вам выдан статус {status} до {subscription_ends_at.strftime("%Y-%m-%d %H:%M:%S")}')

    # start dialog
    if status == 'agency':
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=callback.from_user.id))
        await dialog_manager.start(state=AgencyStateGroup.menu, mode=StartMode.RESET_STACK)
    elif status == 'manager':
        await dialog_manager.start(state=ManagerStateGroup.menu, mode=StartMode.RESET_STACK)
