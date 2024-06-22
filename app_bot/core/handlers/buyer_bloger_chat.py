import logging
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from core.states.buyer_bloger_chat import BuyerBlogerChatStateGroup
from core.keyboards.inline import buyer_bloger_chat_kb

logger = logging.getLogger(__name__)
router = Router(name='Buyer-bloger chat')


@router.callback_query(lambda c: 'send_msg_to_' in c.data)
async def handle_support_from_bloger(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    adv_id = callback.data.split('_')[-1]
    sender_user_id = callback.data.split('_')[-1 - 1]

    await state.set_state(BuyerBlogerChatStateGroup.handle_answer)
    await callback.message.edit_reply_markup(reply_markup=None)

    msg = await callback.message.answer(text='Введите сообщение - оно будет переслано отправителю')

    await state.update_data(
        old_msg_id=msg.message_id, sender_user_id=sender_user_id, adv_id=adv_id,
    )


@router.message(BuyerBlogerChatStateGroup.handle_answer)
async def send_comment_to_bloger(message: types.Message, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    adv_id = state_data['adv_id']
    sender_user_id = state_data['sender_user_id']
    #await bot.delete_message(chat_id=message.chat.id, message_id=state_data['old_msg_id'])

    # send info + msg
    await bot.send_message(
        chat_id=sender_user_id,
        text=f'У вас новое сообщение по рекламе с <b>ID {adv_id}</b>',
    )
    await message.copy_to(
        chat_id=sender_user_id,
        reply_markup=buyer_bloger_chat_kb(sender_user_id=message.from_user.id, adv_id=adv_id),
    )

    # send info
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Сообщение успешно отправлено!',
    )

    await state.clear()
