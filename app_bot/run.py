import asyncio
import core.middlewares
from core.middlewares.ban_middleware import BanMiddleware
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from settings import settings
from setup import register
from core.handlers import routers
from core.dialogs import dialogues
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_album.lock_middleware import LockAlbumMiddleware


bot = Bot(settings.bot_token.get_secret_value(), parse_mode='HTML')

storage = RedisStorage.from_url(
    url=f'redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_name}',
    key_builder=DefaultKeyBuilder(with_destiny=True)
)

dp = Dispatcher(storage=storage)
for _r in routers + dialogues:
    dp.include_router(_r)

setup_dialogs(dp)
core.middlewares.i18n.setup(dp)
LockAlbumMiddleware(router=dp)
dp.message.middleware(BanMiddleware())
dp.callback_query.middleware(BanMiddleware())


async def main():
    async with register():
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
