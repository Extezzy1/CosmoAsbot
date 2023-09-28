import asyncio
import logging

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from middlewares import DbSessionMiddleware
from handlers.commands import commands_router
from handlers.callbacks import callbacks_router
from handlers.admin import admin_router
import config
from database import BaseModel, create_async_engine


async def main():

    url = URL.create(
        "postgresql+asyncpg",
        username=config.PGUSER,
        password=config.PGPASSWORD,
        host=config.IP,
        database=config.DATABASE,
        port=5432

    )

    async_engine = create_async_engine(url)
    session_maker = async_sessionmaker(async_engine, expire_on_commit=True)
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(callbacks_router, commands_router, admin_router)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    # dp.callback_query
    # await proceed_schemas(async_engine, BaseModel.metadata)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

