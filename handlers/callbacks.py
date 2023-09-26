import types
import config
from aiogram import Router, html, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from markups import client_markup as client_markup
from database import User, Subscribe
# from keyboards import generate_balls

callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("buy_rate"))
async def buy_rate(callback: CallbackQuery, session: AsyncSession):
    duration_subscribe = callback.data.split("_")[-2]
