from aiogram.fsm.state import StatesGroup, State


class Contest(StatesGroup):
    start_date = State()
    start_time = State()
    end_date = State()
    end_time = State()
    post_link = State()
    confirmation = State()
