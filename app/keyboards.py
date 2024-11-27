from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import get_all_contests
from app.utils import format_date


class ContestInfoCbData(CallbackData, prefix="contest-info"):
    contest_id: int


class AllContestsCbData(CallbackData, prefix="all_contests"):
    pass


class CompleteContestCbData(CallbackData, prefix="delete-contest"):
    contest_id: int


def get_confirmation_kb() -> ReplyKeyboardMarkup:
    kb_list = [
        [
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет")
        ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


async def build_all_contests_kb(session: AsyncSession, page: int = 0):
    limit = 3
    offset = limit*page
    pg_buttons = []
    contests = await get_all_contests(session=session, offset=offset, limit=limit)
    builder = InlineKeyboardBuilder()

    for contest in contests:
        cb_data = ContestInfoCbData(contest_id=contest.id)
        start_date = format_date(contest.start_time)
        builder.button(
            text=f"{start_date}",
            callback_data=cb_data.pack()
        )
    builder.adjust(5)
    return builder.as_markup()


def build_contest_info_kb(
    contest_id: int,
    is_active: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cb_data_1 = AllContestsCbData()
    builder.button(
        text=f"Все конкурсы",
        callback_data=cb_data_1.pack(),
    )

    if is_active:
        cb_data_2 = CompleteContestCbData(contest_id=contest_id)
        builder.button(
            text=f"Завершить",
            callback_data=cb_data_2.pack(),
        )

    builder.adjust(2)
    return builder.as_markup()


def get_date_kb() -> ReplyKeyboardMarkup:
    today = str(datetime.today()).split()[0]
    today = today.split("-")[1:]
    today = ".".join(today[::-1])
    kb_list = [
        [
            KeyboardButton(text=today),
            KeyboardButton(text="/отмена")
        ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def get_cancel_button() -> ReplyKeyboardMarkup:
    kb_list = [
        [
            KeyboardButton(text="/отмена")
        ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard
