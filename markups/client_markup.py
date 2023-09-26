from aiogram import types

def create_markup_buy_rate():
    buttons = [
        [types.InlineKeyboardButton(text="1 месяц", callback_data="buy_rate_1_month")],
        [types.InlineKeyboardButton(text="6 месяцев", callback_data="buy_rate_6_month")],
        [types.InlineKeyboardButton(text="12 месяцев", callback_data="buy_rate_12_month")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup