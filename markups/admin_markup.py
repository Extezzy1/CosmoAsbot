from aiogram import types

def create_main_markup():
    buttons = [
        [types.InlineKeyboardButton(text="Сформировать выгрузку в формате Excel", callback_data="get_excel")],
        [types.InlineKeyboardButton(text="Статистика", callback_data="stats")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup
