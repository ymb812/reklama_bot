import pytz
from datetime import datetime
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware, types
from aiogram_dialog import DialogManager
from core.database.models import User


class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data['event_from_user']
        dialog_manager: DialogManager = data['dialog_manager']

        message = data['event_update'].message
        callback = data['event_update'].callback_query
        if not message and callback:
            message = callback.message

        user_data = await User.get_or_none(user_id=user.id)
        if not user_data and message.text != '/start':
            await event.bot.send_message(chat_id=data['event_chat'].id, text='Воспользуйтесь /start')
            try:
                await dialog_manager.reset_stack()
            except:
                pass
            return await handler(event, data)

        if user_data and user_data.is_banned:
            return

        # check subscription_ends_at and set None status
        if user_data and user_data.subscription_ends_at and user_data.subscription_ends_at < datetime.now(pytz.timezone('Europe/Moscow')):
            await event.bot.send_message(chat_id=data['event_chat'].id, text='Подписка закончилась. Воспользуйтесь /start')
            user_data.status = None
            await user_data.save()

            try:
                await dialog_manager.reset_stack()
            except:
                pass
            return await handler(event, data)

        return await handler(event, data)
