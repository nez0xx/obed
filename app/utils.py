import random
import string
from datetime import datetime

from app.settings import settings


def validate_date(text: str) -> [bool, list[int]]:
    date = text.split(".")
    if len(date) != 2:
        return False, "Неверный формат даты. Введите дату в формате дд.мм"
    for elem in date:
        if not elem.isdigit():
            return False, "Неверный формат даты. Введите дату заново. Должны использоваться только цифры."

    date = list(map(int, date))

    if date[0] not in range(1, 31) \
            or date[1] not in range(1, 13):
        return False, "Некорректная дата. Введите дату заново. Необходимый формат: [1-31].[1-12]"
    return True, date


def validate_time(text: str) -> [bool, list[int]]:
    time = text.split(":")
    if len(time) != 2:
        return False, "Неверный формат времени. Введите время заново"

    time = list(map(int, time))
    if time[0] not in range(24) or time[1] not in range(60):
        return False, "Неверный формат времени. Введите время заново. Должны использоваться числа 0-23 и 0-59"
    return True, time


def generate_invite_link():

    letters = string.ascii_lowercase
    randstr = ''.join(random.choice(letters) for i in range(7))
    return f"https://t.me/{settings.BOT_LINK}?start={randstr}"


def convert_to_datetime(time: list[int], date: list[int]) -> datetime:
    hour, minute = time[0], time[1]
    day, month = date[0], date[1]
    year = datetime.now().year
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute)


def extract_id(text: str) -> str:
    text = text.split("/")[-1]
    msg_id = text.split("?")[0]
    return msg_id


def format_date(date: datetime) -> str:
    return ".".join(reversed(str(date).split()[0].split("-")))





