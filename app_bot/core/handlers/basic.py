import logging
import asyncio
from aiogram import types, Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode
from core.database.models import User
from core.states.agency import AgencyStateGroup
from core.states.manager import ManagerStateGroup
from core.utils.texts import set_admin_commands, _

logger = logging.getLogger(__name__)
router = Router(name='Basic commands router')


# ez to get id while developing
@router.channel_post(Command(commands=['init']))
@router.message(Command(commands=['init']))
async def init_for_id(message: types.Message):
    await message.delete()
    msg = await message.answer(text=f'<code>{message.chat.id}</code>')
    await asyncio.sleep(2)
    await msg.delete()


# payment handler
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    status = message.successful_payment.invoice_payload

    # set status
    await User.update_data(
        user_id=message.from_user.id,
        username=message.from_user.username,
        status=status
    )
    await message.answer(text=f'Вам выдан статус {status}')

    # start dialog
    if status == 'agency':
        await dialog_manager.start(state=AgencyStateGroup.menu, mode=StartMode.RESET_STACK)
    elif status == 'manager':
        await dialog_manager.start(state=ManagerStateGroup.create_bloger_link, mode=StartMode.RESET_STACK)
