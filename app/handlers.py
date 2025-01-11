from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.database.db_helper import sessionmanager
from app.exceptions import DetailedException
from app.keyboards import get_date_kb, get_cancel_button, get_confirmation_kb, build_all_contests_kb
from app.service import create_contest_service, create_comment_service, get_statistics_service, create_reaction_service
from app.states import Contest
from app.utils import validate_date, validate_time, convert_to_datetime


router = Router(name=__name__)




@router.message(Command("prices", prefix="/!%"))
async def buy_sub(message: types.Message):
    await message.answer("Подписка для участия в конкурсах\n1 месяц - 100руб.\nЧтобы не пополнять счёт каждый месяц, заплатите сразу за несколько месяцев вперёд.")


@router.message(Command("start", prefix="/!%"))
async def start(message: types.Message):
    await message.answer("Привет! Это бот для розыгрышей в комментериях. Оплатите подписку и оставьте комментарий под указанным постом, чтоб получить шанс победить в конкурсе и получить приз")




@router.message(Command("buy", prefix="/!%"))
async def buy_sub(message: types.Message):
    await message.answer("Чтобы продолжить, введите сумму пополнения")


@router.message(Command("cancel", "отмена", prefix="/!%"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено")


@router.message(Command("new", prefix="/!%"))
async def create_contest_handler(message: types.Message, state: FSMContext):
    kb = get_date_kb()
    await state.set_state(Contest.start_date)
    await message.answer("Введите дату начала конкурса в формате дд.мм", reply_markup=kb)


@router.message(Contest.start_date)
async def contest_start_date(message: types.Message, state: FSMContext):
    result = tuple(validate_date(message.text))

    if not result[0]:
        await message.answer(result[1])
        return

    kb = get_cancel_button()

    await state.update_data(start_date=result[1])
    await state.set_state(Contest.start_time)
    await message.answer("Введите время начала конкурса в формате чч:мм\nИспользуйте числа 0-23 и 0-59", reply_markup=kb)


@router.message(Contest.start_time)
async def contest_start_time(message: types.Message, state: FSMContext):
    result = validate_time(message.text)
    if not result[0]:
        await message.answer(result[1])
        return

    kb = get_cancel_button()

    await state.update_data(start_time=result[1])
    await state.set_state(Contest.end_date)
    await message.answer("Введите дату окончания конкурса в формате дд.мм", reply_markup=kb)


@router.message(Contest.end_date)
async def contest_end_date(message: types.Message, state: FSMContext):
    result = validate_date(message.text)
    if not result[0]:
        await message.answer(result[1])
        return

    kb = get_cancel_button()

    await state.update_data(end_date=result[1])
    await state.set_state(Contest.end_time)
    await message.answer(
        text="Введите время окончания конкурса в формате чч:мм\nИспользуйте числа 0-23 и 0-59",
        reply_markup=kb
    )


@router.message(Contest.end_time)
async def contest_end_time(message: types.Message, state: FSMContext):
    result = validate_time(message.text)
    if not result[0]:
        await message.answer(result[1])
        return

    kb = get_cancel_button()

    await state.update_data(end_time=result[1])
    await state.set_state(Contest.post_link)
    await message.answer("Пришлите пост, под которым будут отслеживаться комментарии", reply_markup=kb)


@router.message(Contest.post_link)
async def contest_end_time(message: types.Message, state: FSMContext):
    post_id = None
    if message.forward_origin.message_id:
        data = await state.get_data()
        if "post_id" not in data:
            await state.update_data(post_id=message.forward_origin.message_id)
            kb = get_confirmation_kb()
            await message.answer('Проверьте корректность введённых данных', reply_markup=kb)
            await state.set_state(Contest.confirmation)
        else:
            print(data["post_id"])
    '''
    try:
        post_id = extract_id(message.text)
        await state.update_data(post_id=post_id)
    except Exception as e:
        await message.answer(str(e))
    '''
    print(post_id)


@router.message(Contest.confirmation)
async def contest_confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        print(data)
        start_dt = convert_to_datetime(time=data["start_time"], date=data["start_date"])
        end_dt = convert_to_datetime(time=data["end_time"], date=data["end_date"])

        try:
            post_id = data["post_id"]
            await create_contest_service(start_dt=start_dt, end_dt=end_dt, post_id=post_id)
            await message.answer("Конкурс успешно создан✅")

        except DetailedException as e:
            await message.answer(e.detail)
        await state.clear()

    elif message.text.lower() == "нет":
        await message.answer("Данные сброшены. Создайте конкурс заново✅")
    else:
        kb = get_confirmation_kb()
        await message.answer('Не понял вас. Напишите "Да" или "Нет"', reply_markup=kb)


@router.message(Command("all", prefix="/"))
async def get_winners(message: types.Message):
    async with sessionmanager.session() as session:
        kb = await build_all_contests_kb(session=session)
    await message.answer("🗓Список конкурсов:", reply_markup=kb)


@router.message(Command("stat", prefix="/"))
async def get_stat(message: types.Message):
    data = await get_statistics_service()
    msg = f"""📊Общая статистика:\n🔹Проведенных конкурсов: {data["contests_count"]}
🔹Написанных комментариев: {data["comments_count"]}
🔹Количество победителей: {data["winners_count"]}

"""
    await message.answer(msg)


@router.message_reaction()
async def handle_reaction(message_reaction: types.MessageReactionUpdated):
    if message_reaction.user is None:
        return
    u_id = str(message_reaction.user.id)
    m_id = message_reaction.message_id

    await create_reaction_service(user_id=u_id, message_id=m_id)


@router.message()
async def echo(message: types.Message):
    if message.reply_to_message:
        if message.reply_to_message.forward_from_message_id:
            post_id = message.reply_to_message.forward_from_message_id
            await create_comment_service(
                user_id=str(message.from_user.id),
                message_id=message.message_id,
                post_id=post_id,
                username=message.from_user.username,
                name=message.from_user.full_name
            )
