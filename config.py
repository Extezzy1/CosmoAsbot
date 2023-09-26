import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
IP = str(os.getenv("IP"))

CHANNEL_ID = str(os.getenv("CHANNEL_ID"))


ADMINS = [537373044]

