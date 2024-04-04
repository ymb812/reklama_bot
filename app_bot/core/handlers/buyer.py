import logging
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from core.database.models import User, Advertisement
from core.states.buyer import BuyerStateGroup
from core.utils.texts import _
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Buyer commands router')



@router.callback_query(lambda c: 'buyer_confirm_' in c.data or 'buyer_reject_' in c.data)
async def handle_reklam_from_bloger(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(BuyerStateGroup.handle_reklam_from_bloger)
    await callback.message.delete()

    adv = await Advertisement.get_or_none(id=callback.data.split('_')[-1])
    bloger = await adv.bloger
    if 'confirm_' in callback.data:
        msg = await callback.message.answer(text=_('INPUT_COMMENT'))
        adv.is_done = True

    else:
        msg = await callback.message.answer(text=_('INPUT_CHANGES'))

    await adv.save()
    await state.update_data(
        adv_id=adv.id, bloger_user_id=bloger.user_id, callback_data=callback.data, old_msg_id=msg.message_id
    )


@router.message(BuyerStateGroup.handle_reklam_from_bloger)
async def send_comment_to_bloger(message: types.Message, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    #await bot.delete_message(chat_id=message.chat.id, message_id=state_data['old_msg_id'])

    # send msg to bloger
    if 'confirm_' in state_data['callback_data']:
        await bot.send_message(
            chat_id=state_data['bloger_user_id'],
            text=_('REKLAM_IS_DONE', reklam_id=state_data['adv_id'])
        )
    else:
        await bot.send_message(
            chat_id=state_data['bloger_user_id'],
            text=_('RESPONSE_FROM_BUYER', reklam_id=state_data['adv_id'])
        )

    await message.forward(chat_id=state_data['bloger_user_id'])
    await state.clear()
