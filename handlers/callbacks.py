import types
import config
from aiogram import Router, html, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, InlineQuery
from sqlalchemy import select, update
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from markups import client_markup as client_markup
from database import User, Subscribe, SubProcedures
import FSM

callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("buy_rate"))
async def buy_rate(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    duration_subscribe = callback.data.split("_")[-2]

    query = await session.execute(select(Subscribe).where(Subscribe.user_id == callback.from_user.id and Subscribe.is_active == True))
    user = query.one_or_none()
    if user is not None:
        await callback.message.answer_invoice(
            title=f"Подписка на канал",
            description="Подписка",
            provider_token=config.YOKASSA_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label="Подписка", amount=config.month_1_price)],
            start_parameter="pay",
            payload=f"subscribe_{duration_subscribe}_month",

        )
    else:
        await state.set_state(FSM.FSMClient.get_fio_user)
        await state.update_data(duration=duration_subscribe)
        await callback.message.answer("Введите своё ФИО")


@callbacks_router.callback_query(F.data == "change_data_account")
async def change_data_account(callback: CallbackQuery):
    await callback.message.answer("Что изменяем?", reply_markup=client_markup.create_markup_change_data_account())


@callbacks_router.callback_query(F.data.startswith("change"))
async def change_data(callback: CallbackQuery, state: FSMContext):
    data_split = callback.data.split("_")[-1]
    if data_split == "fio":
        # Изменяем ФИО
        await state.set_state(FSM.FSMClient.get_new_fio)
        await callback.message.answer("Пришли мне новое ФИО")
    elif data_split == "email":
        # Изменяем почту
        await state.set_state(FSM.FSMClient.get_new_email)
        await callback.message.answer("Пришли мне новую почту")
    else:
        # Изменяем телефон
        await state.set_state(FSM.FSMClient.get_new_phone)
        await callback.message.answer("Пришли мне новый телефон")


@callbacks_router.callback_query(F.data == "personal_account")
async def personal_account(callback: CallbackQuery):
    await callback.message.answer_photo(photo=config.file_id_personal_account, reply_markup=client_markup.create_markup_personal_account())


@callbacks_router.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())


@callbacks_router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    await callback.message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())


@callbacks_router.callback_query(F.data == "extend_subscribe")
async def extend_subscribe(callback: CallbackQuery):
    await callback.message.answer("Выберите тариф", reply_markup=client_markup.create_markup_buy_rate())


@callbacks_router.callback_query(F.data == "select_of_code")
async def select_of_code(callback: CallbackQuery):
    await callback.message.answer_photo(photo=config.file_id_select_of_code, reply_markup=client_markup.create_markup_select_of_code())


@callbacks_router.callback_query(F.data.startswith("sub_procedure_"))
async def sub_procedure(callback: CallbackQuery, session: AsyncSession):
    sub_procedure_id = callback.data.split("_")[-1]
    sub_procedure_result = await session.execute(select(SubProcedures).where(SubProcedures.sub_procedure_id == int(sub_procedure_id)))
    sub_procedure = sub_procedure_result.fetchmany(1)[0][0]
    msg = f"Наименование процедуры: <b>{sub_procedure.procedure_subname}</b>\n" \
          f"Номеклатура: <b>{sub_procedure.procedure_code}</b>\n\n" \
          f"Описание: <b>{sub_procedure.procedure_description if sub_procedure.procedure_description is not None else '-'}</b>"
    await callback.message.answer(msg)
