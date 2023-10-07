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

file_id_main_menu = "AgACAgIAAxkBAAICEmUe6Tjud9doHWx4OS1oLxzDhncPAALs0TEbH8j5SCQi0AxhNcQlAQADAgADeAADMAQ"
file_id_personal_account = "AgACAgIAAxkBAAICFGUe6VHieaOMLZLLEGoE6u2vdSFnAALt0TEbH8j5SIy9sB6x5i4SAQADAgADeAADMAQ"
file_id_memo = "AgACAgIAAxkBAAICFWUe6VtIHsuI1wTBib2VT8HtBWr7AALu0TEbH8j5SAF8uay4XY2DAQADAgADeAADMAQ"
file_id_select_of_code = "AgACAgIAAxkBAAICFmUe6Wf5eeoKUbd8capj2X6_pCWNAALv0TEbH8j5SKA7Ee-_hzkUAQADAgADeAADMAQ"
file_id_atlas = "AgACAgIAAxkBAAICF2Ue6XFSl1h9GUJvQ4hOR0Ewax7gAALw0TEbH8j5SKoOtUo41UFTAQADAgADeAADMAQ"

ADMINS = [537373044, 381063457]

