import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
IP = str(os.getenv("IP"))

CHANNEL_ID = str(os.getenv("CHANNEL_ID"))
YOKASSA_TOKEN = str(os.getenv("YOKASSA_TOKEN"))
month_1_price = 50000

file_id_main_menu = "AgACAgIAAxkBAAOdZRR_3smmh-zOogdWULtAUrQis_UAAsHOMRtm26BId2XHAgNux2oBAAMCAAN5AAMwBA"
file_id_personal_account = "AgACAgIAAxkBAAOeZRR__0liPxfU4pUa5JqnNSwUlhEAAsPOMRtm26BImnnkprM8dMcBAAMCAAN5AAMwBA"
file_id_memo = "AgACAgIAAxkBAAOfZRSAEuMlAoWmYmhtP-Oodz3RgrgAAsXOMRtm26BINa5Ar-KPkEkBAAMCAAN5AAMwBA"
file_id_select_of_code = "AgACAgIAAxkBAAOgZRSAHlCpCihec6ug8F12zm6z3fMAAsbOMRtm26BIfTjFwF9LaUoBAAMCAAN5AAMwBA"
file_id_atlas = "AgACAgIAAxkBAAOhZRSAMKEI4-szcpsegYyb-qyjlaoAAsfOMRtm26BIuK-u61q6fesBAAMCAAN5AAMwBA"

ADMINS = [537373044, ]

