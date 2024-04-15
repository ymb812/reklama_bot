import logging
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from core.database.models import User, Advertisement
from core.states.manager import ManagerStateGroup
from core.utils.texts import _
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Bloger support router')


@router.callback_query(lambda c: 'answer_' in c.data)
async def handle_support_from_bloger(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(ManagerStateGroup.handle_support)
    await callback.message.edit_reply_markup(reply_markup=None)

    adv = await Advertisement.get_or_none(id=callback.data.split('_')[-1])
    bloger = await adv.bloger
    msg = await callback.message.answer(text=_('INPUT_ANSWER'))

    await state.update_data(
        adv_id=adv.id, bloger_user_id=bloger.user_id, old_msg_id=msg.message_id
    )


@router.message(ManagerStateGroup.handle_support)
async def send_comment_to_bloger(message: types.Message, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    #await bot.delete_message(chat_id=message.chat.id, message_id=state_data['old_msg_id'])

    # send msg to bloger
    await bot.send_message(
        chat_id=state_data['bloger_user_id'],
        text=_('MANAGER_ANSWER_SUPPORT', reklam_id=state_data['adv_id'])
    )

    await message.copy_to(chat_id=state_data['bloger_user_id'])
    await state.clear()
