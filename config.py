import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
IP = str(os.getenv("IP"))

CHANNEL_ID = str(os.getenv("CHANNEL_ID"))
CHANNEL_LINK = str(os.getenv("CHANNEL_LINK"))
YOKASSA_TOKEN = str(os.getenv("YOKASSA_TOKEN"))
month_1_price = 29900
month_6_price = 150000
month_12_price = 290000

file_id_main_menu = "AgACAgIAAxkBAAICEmUe6Tjud9doHWx4OS1oLxzDhncPAALs0TEbH8j5SCQi0AxhNcQlAQADAgADeAADMAQ"
file_id_personal_account = "AgACAgIAAxkBAAICFGUe6VHieaOMLZLLEGoE6u2vdSFnAALt0TEbH8j5SIy9sB6x5i4SAQADAgADeAADMAQ"
file_id_memo = "AgACAgIAAxkBAAIHRmUmWo5A2yfPhz8rHoHhs-R-bUe-AAJI0jEbmqMwSZx4CUVaHcBgAQADAgADeAADMAQ"
file_id_select_of_code = "AgACAgIAAxkBAAIHR2UmWregGzGuKwABhFfMvdABh4Ve1gACc8oxGyNUMEkVIYSjtkbZwQEAAwIAA3gAAzAE"
file_id_atlas = "AgACAgIAAxkBAAIHSGUmWsAGoHoNCOiknWSEYqjxmbTRAAJJ0jEbmqMwSZhyfHiwdGmsAQADAgADeAADMAQ"
file_id_change_data = "AgACAgIAAxkBAAICT2UipekE_mY4hLyPh7o58wABUes8igACCtAxG5bXEEnlf11NZdDGAQEAAwIAA3gAAzAE"
file_id_select_rate = "AgACAgIAAxkBAAICUGUipfwToCwmJxk2hik_xY9YvJgRAAIL0DEbltcQSZ_4Aox_KELDAQADAgADeAADMAQ"


ADMINS = [537373044, 381063457]

