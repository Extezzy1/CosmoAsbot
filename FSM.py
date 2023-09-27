from aiogram.fsm.state import StatesGroup, State


class FSMClient(StatesGroup):
    get_fio_user = State()
    get_email = State()
    get_phone = State()