import types
import config
from aiogram import Router, html, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from markups import client_markup as client_markup
from database import User, Subscribe
# from keyboards import generate_balls

commands_router = Router()


@commands_router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot):
    user_channel = await bot.get_chat_member(config.CHANNEL_ID, message.from_user.id)
    if user_channel.status == "left":
        await message.answer("Пожалуйста, подпишитесь на канал")
        user = User(user_id=message.from_user.id)
        await session.merge(user)
    else:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.one_or_none()
        if user is not None:
            await session.execute(update(User).where(User.user_id == message.from_user.id).values(is_subscribe=True))

        else:
            user = User(user_id=message.from_user.id, is_subscribe=True)
            await session.merge(user)

        result = await session.execute(
            select(Subscribe).where(Subscribe.user_id == message.from_user.id and Subscribe.is_active == True))
        subscribe = result.one_or_none()
        if subscribe is not None:
            # Вывод главного меню
            pass
        else:
            # Предложение купить подписку
            await message.answer("Выберите тариф", reply_markup=client_markup.create_markup_buy_rate())


    await session.commit()
    # await message.answer("Hello!")

