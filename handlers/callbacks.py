import os
import types

import aiogram.types

import config
from aiogram import Router, html, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, InlineQuery
from sqlalchemy import select, update
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from markups import client_markup as client_markup
from database import User, Subscribe, SubProcedures, Memo
import FSM
from utils import create_pdf_file, merge_pdf_files

callbacks_router = Router()


@callbacks_router.callback_query(F.data == "check_subscribe")
async def check_subscribe(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    user_channel = await bot.get_chat_member(config.CHANNEL_ID, callback.from_user.id)
    if user_channel.status == "left":
        await callback.message.answer("Пожалуйста, подпишитесь на канал", reply_markup=client_markup.create_markup_link_to_channel())
    else:
        print(callback.from_user.id)
        await session.execute(update(User).where(User.user_id == callback.from_user.id).values(is_subscribe=True))
        result = await session.execute(
            select(Subscribe).where(Subscribe.user_id == callback.from_user.id and Subscribe.is_active == True))
        subscribe = result.one_or_none()
        if subscribe is not None:
            # Вывод главного меню
            await callback.message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())
        else:
            # Предложение купить подписку
            await callback.message.answer("Выберите тариф", reply_markup=client_markup.create_markup_buy_rate())

    await session.commit()


@callbacks_router.callback_query(F.data.startswith("buy_rate"))
async def buy_rate(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    duration_subscribe = int(callback.data.split("_")[-2])

    query = await session.execute(select(Subscribe).where(Subscribe.user_id == callback.from_user.id and Subscribe.is_active == True))
    user = query.one_or_none()
    if user is not None:
        if duration_subscribe == 1:
            price = config.month_1_price
            description = "Подписка на 1 месяц"
        elif duration_subscribe == 6:
            price = config.month_6_price
            description = "Подписка на 6 месяцев"
        else:
            price = config.month_12_price
            description = "Подписка на 12 месяцев"
        await callback.message.answer_invoice(
            title=f"Подписка CosmoAS",
            description=description,
            provider_token=config.YOKASSA_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label="Подписка", amount=price)],
            start_parameter="pay",
            payload=f"subscribe_{duration_subscribe}_month",

        )
    else:
        await state.set_state(FSM.FSMClient.get_fio_user)
        await state.update_data(duration=duration_subscribe)
        await callback.message.answer("Введите своё ФИО")


@callbacks_router.callback_query(F.data == "change_data_account")
async def change_data_account(callback: CallbackQuery):
    await callback.message.answer_photo(photo=config.file_id_change_data, reply_markup=client_markup.create_markup_change_data_account())


@callbacks_router.callback_query(F.data.startswith("change"))
async def change_data(callback: CallbackQuery, state: FSMContext):
    data_split = callback.data.split("_")[-1]
    if data_split == "fio":
        # Изменяем ФИО
        await state.set_state(FSM.FSMClient.get_new_fio)
        msg = await callback.message.answer("Пришли мне новое ФИО")
        await state.set_data({"msgs_id_delete": [msg.message_id]})

    elif data_split == "email":
        # Изменяем почту
        await state.set_state(FSM.FSMClient.get_new_email)
        msg = await callback.message.answer("Пришли мне новую почту")
        await state.set_data({"msgs_id_delete": [msg.message_id]})

    else:
        # Изменяем телефон
        await state.set_state(FSM.FSMClient.get_new_phone)
        msg = await callback.message.answer("Пришли мне новый телефон")
        await state.set_data({"msgs_id_delete": [msg.message_id]})


@callbacks_router.callback_query(F.data == "personal_account")
async def personal_account(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer_photo(photo=config.file_id_personal_account, reply_markup=client_markup.create_markup_personal_account())


@callbacks_router.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())


@callbacks_router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msgs_id_delete: list = data.get("msgs_id_delete", False)
    if msgs_id_delete:
        for msg in msgs_id_delete:
            try:
                await bot.delete_message(callback.from_user.id, msg)
            except Exception as ex:
                print(ex)
    await state.clear()
    await callback.message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())


@callbacks_router.callback_query(F.data == "extend_subscribe")
async def extend_subscribe(callback: CallbackQuery):
    await callback.message.answer_photo(photo=config.file_id_select_rate, reply_markup=client_markup.create_markup_buy_rate())


@callbacks_router.callback_query(F.data == "select_of_code")
async def select_of_code(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer_photo(photo=config.file_id_select_of_code, reply_markup=client_markup.create_markup_select_of_code())
    await state.set_state(FSM.FSMClient.select_of_codes)


@callbacks_router.callback_query(F.data.startswith("sub_procedure_"))
async def sub_procedure(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    sub_procedure_id = callback.data.split("_")[-1]
    sub_procedure_result = await session.execute(select(SubProcedures).where(SubProcedures.sub_procedure_id == int(sub_procedure_id)))
    sub_procedure = sub_procedure_result.fetchmany(1)[0][0]
    caption = f"Наименование процедуры: <b>{sub_procedure.procedure_subname}</b>\n" \
          f"Номеклатура: <b>{sub_procedure.procedure_code}</b>\n\n" \
          f"Описание: <b>{sub_procedure.procedure_description if sub_procedure.procedure_description is not None else '-'}</b>"
    msg = await callback.message.answer(caption, reply_markup=client_markup.create_markup_back_to_main_menu())
    data = await state.get_data()
    data["msgs_id_delete"].append(msg.message_id)
    await state.set_data(data)


@callbacks_router.callback_query(F.data.startswith("atlas"))
async def atlas(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer_photo(photo=config.file_id_atlas, reply_markup=client_markup.create_markup_atlas())
    await state.set_state(FSM.FSMClient.atlas)


@callbacks_router.callback_query(F.data.startswith("memo"))
async def memo(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer_photo(photo=config.file_id_memo, reply_markup=client_markup.create_markup_atlas())
    await state.set_state(FSM.FSMClient.memo)


@callbacks_router.callback_query(F.data == "add_comment")
async def add_comment(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSM.FSMClient.add_comment)
    msg = await callback.message.answer("Введите комментарий")
    data = await state.get_data()
    if not data.get("msgs_id_delete", False):
        data["msgs_id_delete"] = [msg.message_id]
    else:
        data["msgs_id_delete"].append(msg.message_id)
    await state.set_data(data)


@callbacks_router.callback_query(F.data == "accept")
async def accept(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer("Отлично!", reply_markup=client_markup.create_markup_memo_create_pdf())
    data = await state.get_data()
    if not data.get("msgs_id_delete", False):
        data["msgs_id_delete"] = [msg.message_id]
    else:
        data["msgs_id_delete"].append(msg.message_id)
    await state.set_data(data)


@callbacks_router.callback_query(F.data == "create_pdf")
async def create_pdf(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    memo_ids = data["memo_id"]
    msg_id = (await callback.message.answer("Ожидайте, файл формируется...")).message_id
    doctor_result = await session.execute(select(User).where(User.user_id == callback.from_user.id))
    doctor_full_name = doctor_result.one_or_none()[0].fio
    pdfs = []
    print(memo_ids)
    for index, memo_id in enumerate(memo_ids, 1):
        print(index, memo_id)
        memo_result = await session.execute(select(Memo).where(Memo.memo_id == memo_id))
        memo_result_ = memo_result.one_or_none()[0]
        memo_text = memo_result_.memo_text
        memo_title = memo_result_.memo_title
        comment = data.get(f"comment_{memo_id}", "")
        pdf = create_pdf_file(memo_title, memo_text, doctor_full_name, comment, callback.from_user.id, index)
        pdfs.append(pdf)

    total_pdf = merge_pdf_files(pdfs, callback.from_user.id)
    msg = await callback.message.answer_document(document=aiogram.types.FSInputFile(total_pdf), reply_markup=client_markup.create_markup_back_to_main_menu())

    data = await state.get_data()
    if not data.get("msgs_id_delete", False):
        data["msgs_id_delete"] = [msg.message_id]
    else:
        data["msgs_id_delete"].append(msg.message_id)

    await state.set_data(data)

    for pdf in pdfs:
        os.remove(pdf)
    os.remove(total_pdf)

    await bot.delete_message(callback.from_user.id, msg_id)


@callbacks_router.callback_query(F.data == "add_procedure")
async def add_procedure(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_photo(photo=config.file_id_memo, reply_markup=client_markup.create_markup_atlas())
