from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware, types
from core.database.models import User


class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data['event_from_user']
        user_data = await User.get_or_none(user_id=user.id)
        if user_data and user_data.is_banned:
            return

        return await handler(event, data)
