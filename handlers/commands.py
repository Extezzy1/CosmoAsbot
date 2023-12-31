import datetime
import types
from random import randrange

from aiogram.utils.media_group import MediaGroupBuilder

import FSM
import config
from aiogram import Router, html, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, ContentType, InlineQuery, InlineQueryResultArticle, \
    InputTextMessageContent
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from markups import client_markup as client_markup
from database import User, Subscribe, Payments, Procedures, SubProcedures, Atlas, AtlasPhotos, Memo, MemoProcedure
from email_validate import validate
import phonenumbers


commands_router = Router()


@commands_router.message(F.photo)
async def get_photo(message: Message):
    print(message.photo)


@commands_router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot):
    user_channel = await bot.get_chat_member(config.CHANNEL_ID, message.from_user.id)
    if user_channel.status == "left":
        await message.answer("Пожалуйста, подпишитесь на канал", reply_markup=client_markup.create_markup_link_to_channel())
        user = User(user_id=message.from_user.id, username=message.from_user.username)
        await session.merge(user)
    else:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.one_or_none()
        if user is not None:
            await session.execute(update(User).where(User.user_id == message.from_user.id).values(is_subscribe=True))

        else:
            user = User(user_id=message.from_user.id, username=message.from_user.username, is_subscribe=True)
            await session.merge(user)

        result = await session.execute(
            select(Subscribe).where(Subscribe.user_id == message.from_user.id and Subscribe.is_active == True))
        subscribe = result.one_or_none()
        if subscribe is not None:
            # Вывод главного меню
            await message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())
        else:
            # Предложение купить подписку
            await message.answer("Выберите тариф", reply_markup=client_markup.create_markup_buy_rate())

    await session.commit()
    # await message.answer("Hello!")


@commands_router.message(FSM.FSMClient.get_fio_user)
async def get_fio_user(message: Message, state: FSMContext) -> None:
    user_fio = message.text.strip()
    await state.update_data(user_fio=user_fio)
    await state.set_state(FSM.FSMClient.get_email)
    await message.answer("Теперь введите свою электронную почту")


@commands_router.message(FSM.FSMClient.get_email)
async def get_email_user(message: Message, state: FSMContext) -> None:
    email = message.text.strip()
    is_validate = validate(
        email_address=email.strip(),
        check_format=True,
        check_blacklist=False,
        check_dns=False,
        dns_timeout=10,
        check_smtp=False,
        smtp_debug=False)
    if is_validate:
        await state.update_data(email=email)
        await state.set_state(FSM.FSMClient.get_phone)
        await message.answer("Теперь введите свой номер телефона (+7...)")
    else:
        await message.answer("Электронная почта неверного формата, повторите ввод!")


@commands_router.message(FSM.FSMClient.get_phone)
async def get_phone_user(message: Message, state: FSMContext, session: AsyncSession) -> None:
    phone = message.text.strip()
    if phone[0] == '8':
        phone = '+7' + phone[1:]
    try:
        phone_number = phonenumbers.parse(phone)
        if phonenumbers.is_valid_number(phone_number):
            # Создаем тикет для оплаты
            data = await state.get_data()
            duration_subscribe = int(data["duration"])
            if duration_subscribe == 1:
                price = config.month_1_price
                description = "Подписка на 1 месяц"
            elif duration_subscribe == 6:
                price = config.month_6_price
                description = "Подписка на 6 месяцев"
            else:
                price = config.month_12_price
                description = "Подписка на 12 месяцев"
            await message.answer_invoice(
                title=f"Подписка CosmoAS",
                description=description,
                provider_token=config.YOKASSA_TOKEN,
                currency="RUB",
                prices=[LabeledPrice(label="Подписка", amount=price)],
                start_parameter="pay",
                payload=f"subscribe_{duration_subscribe}_month",

            )

            # Обновляем данные пользователя
            await session.execute(update(User).where(User.user_id == message.from_user.id).values(fio=data["user_fio"], phone=phone, email=data["email"]))
            await session.commit()
            await state.clear()
        else:
            await message.answer("Введите корректный номер телефона!")
    except Exception as ex:
        print(ex)
        await message.answer("Введите корректный номер телефона!")


@commands_router.pre_checkout_query()
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(
        ok=True,
        error_message="Что-то пошло не так, попробуйте еще раз"
    )


@commands_router.message(F.successful_payment)
async def successful_payment(message: Message, session: AsyncSession):
    payload = message.successful_payment.invoice_payload
    count_month = payload.split("_")[-2]
    value = message.successful_payment.total_amount / 100
    await session.merge(Payments(user_id=message.from_user.id, value=value))
    result = await session.execute(select(Subscribe).where(Subscribe.user_id == message.from_user.id and Subscribe.is_active == True))
    is_subscribe = result.one_or_none()
    if is_subscribe is None:
        # Добавляем подписку пользователя
        await session.merge(Subscribe(user_id=message.from_user.id, date_end=datetime.datetime.now() + datetime.timedelta(days=30 * int(count_month))))
        await message.answer("Вы успешно оплатили подписку!")
        await message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())
    else:
        # Продляем подписку
        await session.execute(update(User).where(User.user_id == message.from_user.id).values(is_subscribe=True))
        await session.execute(update(Subscribe).where(Subscribe.user_id == message.from_user.id and Subscribe.is_active == True).values(date_end=Subscribe.date_end + datetime.timedelta(days=30 * int(count_month))))
        await message.answer("Ваша подписка продлена")
        await message.answer_photo(photo=config.file_id_main_menu, reply_markup=client_markup.create_markup_main_menu())
    await session.commit()


@commands_router.message(FSM.FSMClient.get_new_fio)
async def change_fio(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    fio = message.text.strip()
    await session.execute(update(User).where(User.user_id == message.from_user.id).values(fio=fio))
    await message.delete()
    await message.answer_photo(photo=config.file_id_change_data, caption="ФИО было успешно изменено!", reply_markup=client_markup.create_markup_change_data_account())
    data = await state.get_data()
    msgs_id_delete: list = data.get("msgs_id_delete", False)
    if msgs_id_delete:
        for msg in msgs_id_delete:
            try:
                await bot.delete_message(message.from_user.id, msg)
            except Exception as ex:
                print(ex)
    await state.clear()
    await session.commit()


@commands_router.message(FSM.FSMClient.get_new_email)
async def change_email(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    email = message.text.strip()
    is_validate = validate(
        email_address=email.strip(),
        check_format=True,
        check_blacklist=False,
        check_dns=False,
        dns_timeout=10,
        check_smtp=False,
        smtp_debug=False)
    if is_validate:
        await session.execute(update(User).where(User.user_id == message.from_user.id).values(email=email))
        await message.delete()
        await message.answer_photo(photo=config.file_id_change_data, caption="Почта была успешно изменена!",
                                   reply_markup=client_markup.create_markup_change_data_account())
        data = await state.get_data()
        msgs_id_delete: list = data.get("msgs_id_delete", False)
        if msgs_id_delete:
            for msg in msgs_id_delete:
                try:
                    await bot.delete_message(message.from_user.id, msg)
                except Exception as ex:
                    print(ex)
        # await message.answer("Почта была успешно изменена!",
        #                      reply_markup=client_markup.create_markup_change_data_account())
        await state.clear()
        await session.commit()
    else:
        await message.answer("Электронная почта неверного формата, повторите ввод!")


@commands_router.message(FSM.FSMClient.get_new_phone)
async def change_phone(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    phone = message.text.strip()
    try:
        phone_number = phonenumbers.parse(phone)
        if phonenumbers.is_valid_number(phone_number):
            # Обновляем данные пользователя
            await session.execute(update(User).where(User.user_id == message.from_user.id).values(phone=phone))
            await message.delete()
            await message.answer_photo(photo=config.file_id_change_data, caption="Телефон был успешно изменен!",
                                       reply_markup=client_markup.create_markup_change_data_account())
            data = await state.get_data()
            msgs_id_delete: list = data.get("msgs_id_delete", False)
            if msgs_id_delete:
                for msg in msgs_id_delete:
                    try:
                        await bot.delete_message(message.from_user.id, msg)
                    except Exception as ex:
                        print(ex)
            # await message.answer("Телефон был успешно изменен!",
            #                      reply_markup=client_markup.create_markup_change_data_account())
            await session.commit()
            await state.clear()
        else:
            await message.answer("Введите корректный номер телефона!")
    except Exception as ex:
        print(ex)
        await message.answer("Введите корректный номер телефона!")


@commands_router.inline_query(FSM.FSMClient.select_of_codes)
async def select_of_codes(query: InlineQuery, session: AsyncSession, state: FSMContext):
    query_text_split = query.query.split(" ")
    query_answer_items = []
    procedures_result = await session.execute(select(Procedures))
    all_procedures = procedures_result.fetchall()

    for word in query_text_split:
        print(word)
        for item in all_procedures:
            if word.lower() in item[0].procedure_name.lower():
                query_answer_items.append(item[0])

    articles = []
    query_answer_items = sorted(query_answer_items, key=lambda x: x.procedure_name)
    for item in query_answer_items:
        # if len(articles) <= 9:
        #
        #     articles.append(InlineQueryResultArticle(
        #         id=str(randrange(1, 999999999)),
        #         title=item.procedure_name,
        #         input_message_content=InputTextMessageContent(message_text=f'/adProc {item.procedure_name}')
        #     ))
        # else:
        #     break
        articles.append(InlineQueryResultArticle(
            id=str(randrange(1, 999999999)),
            title=item.procedure_name,
            input_message_content=InputTextMessageContent(message_text=f'/adProc {item.procedure_name}')
        ))
    await query.answer(articles, cache_time=1, is_personal=True)


@commands_router.message(Command("adProc"))
async def adProc(message: Message, session: AsyncSession, state: FSMContext):
    text = message.text
    text_without_command = " ".join(text.split(" ")[1:])
    procedure_id_result = await session.execute(select(Procedures).where(Procedures.procedure_name == text_without_command))
    procedure_id = procedure_id_result.fetchmany(1)[0][0].procedure_id
    sub_procedures_result = await session.execute(select(SubProcedures).where(SubProcedures.procedure_id == procedure_id))
    sub_procedures = sub_procedures_result.fetchall()
    data = await state.get_data()
    data["msgs_id_delete"].append(message.message_id)
    if len(sub_procedures) > 1:
        msg = await message.answer("Выберите подпроцедуру", reply_markup=client_markup.create_markup_subprocedures(sub_procedures))
        msgs_id_delete = data.get("msgs_id_delete", False)
        if not msgs_id_delete:
            data["msgs_id_delete"] = []
        data["msgs_id_delete"].append(msg.message_id)
        await state.set_data(data)
    else:
        sub_procedure = sub_procedures[0][0]
        caption = f"Наименование процедуры: <b>{sub_procedure.procedure_subname}</b>\n" \
              f"Номеклатура: <b>{sub_procedure.procedure_code}</b>\n\n" \
              f"Описание: <b>{sub_procedure.procedure_description if sub_procedure.procedure_description is not None else '-'}</b>"
        await message.answer(caption, reply_markup=client_markup.create_markup_back_to_main_menu())


@commands_router.inline_query(FSM.FSMClient.atlas)
async def atlas(query: InlineQuery, session: AsyncSession, state: FSMContext):
    query_text_split = query.query.split(" ")
    query_answer_items = []
    atlas_result = await session.execute(select(Atlas))
    all_atlas_entries = atlas_result.fetchall()

    for word in query_text_split:
        print(word)
        for item in all_atlas_entries:

            if word.lower() in item[0].atlas_entry_text.lower():
                query_answer_items.append(item[0])

    articles = []
    query_answer_items = sorted(query_answer_items, key=lambda x: x.atlas_entry_text)
    for item in query_answer_items:
        # if len(articles) <= 9:
        #     articles.append(InlineQueryResultArticle(
        #         id=str(randrange(1, 999999999)),
        #         title=item.atlas_entry_text,
        #         input_message_content=InputTextMessageContent(message_text=f'/adSubj {item.atlas_entry_text}')
        #     ))
        # else:
        #     break
        articles.append(InlineQueryResultArticle(
            id=str(randrange(1, 999999999)),
            title=item.atlas_entry_text,
            input_message_content=InputTextMessageContent(message_text=f'/adSubj {item.atlas_entry_text}')
        ))
    await query.answer(articles, cache_time=1, is_personal=True)


@commands_router.message(Command("adSubj"))
async def adSubj(message: Message, session: AsyncSession, state: FSMContext):

    text = message.text
    text_without_command = " ".join(text.split(" ")[1:])
    atlas_entry_result = await session.execute(select(Atlas).where(Atlas.atlas_entry_text == text_without_command))
    atlas_entry_id = atlas_entry_result.fetchmany(1)[0][0].atlas_entry_id
    atlas_photos_result = await session.execute(select(AtlasPhotos).where(AtlasPhotos.altas_entry_id == atlas_entry_id))
    atlas_photos = atlas_photos_result.fetchall()

    media_group = MediaGroupBuilder()
    for photo in atlas_photos:
        media_group.add_photo(media=photo[0].atlas_photo_id)

    msg_id = await message.answer_media_group(media_group.build())
    data = await state.get_data()
    msgs_id_delete = data.get("msgs_id_delete", False)
    if not msgs_id_delete:
        data["msgs_id_delete"] = []
    for msg in msg_id:
        data["msgs_id_delete"].append(msg.message_id)
    data["msgs_id_delete"].append(message.message_id)
    await state.set_data(data)
    await message.answer(text="Нажмите на кнопку, чтобы вернуться в главное меню", reply_markup=client_markup.create_markup_back_to_main_menu())


@commands_router.inline_query(FSM.FSMClient.memo)
async def memo(query: InlineQuery, session: AsyncSession, state: FSMContext):
    query_text_split = query.query.split(" ")
    query_answer_items = []
    procedures_result = await session.execute(select(MemoProcedure))
    all_procedures = procedures_result.fetchall()

    for word in query_text_split:
        print(word)
        for item in all_procedures:
            if word.lower() in item[0].procedure_title.lower():
                query_answer_items.append(item[0])

    articles = []
    query_answer_items = sorted(query_answer_items, key=lambda x: x.procedure_title)
    for item in query_answer_items:
        # if len(articles) <= 9:
        #
        #     articles.append(InlineQueryResultArticle(
        #         id=str(randrange(1, 999999999)),
        #         title=item.procedure_title,
        #         input_message_content=InputTextMessageContent(message_text=f'/adProcMemo {item.procedure_title}')
        #     ))
        # else:
        #     break
        articles.append(InlineQueryResultArticle(
            id=str(randrange(1, 999999999)),
            title=item.procedure_title,
            input_message_content=InputTextMessageContent(message_text=f'/adProcMemo {item.procedure_title}')
        ))
    await query.answer(articles, cache_time=1, is_personal=True)


@commands_router.message(Command("adProcMemo"))
async def adProcMemo(message: Message, session: AsyncSession, state: FSMContext):
    text = message.text
    text_without_command = " ".join(text.split(" ")[1:])
    procedure_id_result = await session.execute(select(MemoProcedure).where(MemoProcedure.procedure_title == text_without_command))
    procedure_id = procedure_id_result.fetchmany(1)[0][0].procedure_id
    # Вывод текста рекомендации
    memo_result = await session.execute(select(Memo).where(Memo.procedure_id == procedure_id))
    memo_result_ = memo_result.fetchall()[0][0]
    memo_text = memo_result_.memo_text
    memo_title = memo_result_.memo_title

    data = await state.get_data()
    data["msgs_id_delete"].append(message.message_id)
    print(data)
    if not data.get("memo_id", False):
        data["memo_id"] = [memo_result_.memo_id]
    else:
        data["memo_id"].append(memo_result_.memo_id)
    msg = await message.answer(f"<b><u>{memo_title}</u></b>\n\n" + memo_text, parse_mode="HTML", reply_markup=client_markup.create_markup_memo_recommendations())
    data["msgs_id_delete"].append(msg.message_id)

    await state.set_data(data)


@commands_router.message(FSM.FSMClient.add_comment)
async def get_comment(message: Message, state: FSMContext):
    comment_text = message.text.strip()
    data = await state.get_data()
    last_memo_id = data["memo_id"][-1]
    data[f"comment_{last_memo_id}"] = comment_text
    await state.set_state(FSM.FSMClient.memo)
    msg = await message.answer("Отлично!", reply_markup=client_markup.create_markup_memo_create_pdf())
    data["msgs_id_delete"].append(msg.message_id)
    data["msgs_id_delete"].append(message.message_id)
    await state.set_data(data)
