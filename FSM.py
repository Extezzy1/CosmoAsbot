from aiogram.fsm.state import StatesGroup, State


class FSMClient(StatesGroup):
    get_fio_user = State()
    get_email = State()
    get_phone = State()

    get_new_fio = State()
    get_new_email = State()
    get_new_phone = State()