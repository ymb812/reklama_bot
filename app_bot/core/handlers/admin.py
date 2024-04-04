import json
import logging
from aiogram import types, Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from broadcaster import Broadcaster
from core.database.models import User, StatusType
from core.keyboards.inline import mailing_kb
from core.states.mailing import MailingStateGroup
from core.utils.texts import _, set_admin_commands
from core.excel.excel_generator import create_excel
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Admin commands router')



# admin login
@router.message(Command(commands=['admin']))
async def admin_login(message: types.Message, state: FSMContext, command: CommandObject, bot: Bot):
    if command.args == settings.admin_password.get_secret_value():
        await state.clear()
        await message.answer(text=_('NEW_ADMIN_TEXT'))
        await User.set_status(user_id=message.from_user.id, status='admin')
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))


@router.message(Command(commands=['send']))
async def start_of_mailing(message: types.Message, state: FSMContext):
    user = await User.get_or_none(user_id=message.from_user.id)
    if not user or user.status != StatusType.agency:
        await message.answer(_('SEND_NOT_ALLOWED'))
        return

    await state.clear()

    await message.answer(_('INPUT_MAILING_CONTENT'))
    await state.set_state(MailingStateGroup.content_input)


@router.message(MailingStateGroup.content_input)
async def confirm_mailing(message: types.Message, state: FSMContext):
    msg = await message.answer(text=_('CONFIRM_MAILING'), reply_markup=mailing_kb())
    await state.update_data(content=message.model_dump_json(exclude_defaults=True), old_msg_id=msg.message_id)


@router.callback_query(
    lambda c: 'start_manager_mailing' in c.data or 'start_bloger_mailing' in c.data,
    MailingStateGroup.content_input
)
async def admin_team_approve_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=state_data['old_msg_id'])

    # manager or bloger mailing
    if callback.data == 'start_manager_mailing':
        status = StatusType.manager
    else:
        status = StatusType.bloger

    text = _('MAILING_HAS_BEEN_STARTED', admin_username=callback.from_user.username)
    await callback.message.answer(text=text)

    sent_amount = await Broadcaster.send_content_to_users(
        bot=bot,
        message=types.Message(**json.loads(state_data['content'])),
        status=status,
        agency_or_manager_user_id=callback.from_user.id,
    )
    await state.clear()
    await callback.message.answer(text=_('MAILING_IS_COMPLETED', sent_amount=sent_amount))


@router.message(Command(commands=['stats']))
async def excel_stats(message: types.Message):
    # cuz command is only for 'admin'
    user = await User.get(user_id=message.from_user.id)
    if user.status != 'admin':
        return

    file_in_memory = await create_excel(model=User)
    await message.answer_document(document=types.BufferedInputFile(file_in_memory.read(), filename=settings.excel_file))
