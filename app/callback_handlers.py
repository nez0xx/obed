from datetime import datetime

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

from app.crud import get_contest_by_id, count_participicants, get_comments_by_contest_id
from app.database.db_helper import sessionmanager
from app.keyboards import build_all_contests_kb, build_contest_info_kb, AllContestsCbData, ContestInfoCbData, \
    CompleteContestCbData
from app.service import get_contest_winners_service, complete_contest_service
from app.utils import format_date

router = Router(name=__name__)


@router.callback_query(ContestInfoCbData.filter())
async def contest_info_callback(
    callback_query: CallbackQuery,
    callback_data: ContestInfoCbData
):
    session = sessionmanager.session()

    contest_id = callback_data.contest_id
    contest = await get_contest_by_id(session=session, contest_id=contest_id)

    now = datetime.now()
    is_active = contest.start_time < now < contest.end_time

    winners = await get_contest_winners_service(contest_id=contest_id)
    winners_count = len(winners)
    winners = ("\n".join([f"@{winners[key].username} - {key}" for key in winners])
               .replace("likes", "лайки")
               .replace('random', 'рандом')
               .replace('under', 'комментарий под победедителем'))
    start_date = format_date(contest.start_time)
    end_date = format_date(contest.end_time)

    participicants = await count_participicants(session=session, contest_id=contest_id)
    comms = len(await get_comments_by_contest_id(session=session, contest_id=contest_id))

    msg = f"""
📗Информация о конкурсе
📅Дата начала: {start_date}
📅Дата окончания: {end_date}
🧑🏻Количество участников: {participicants}
✉️Количество комментариев: {comms}
🏆Победители: 
{winners}
"""
    await session.close()
    kb = build_contest_info_kb(contest_id=contest_id, is_active=is_active)
    await callback_query.message.edit_text(msg, reply_markup=kb)


@router.callback_query(AllContestsCbData.filter())
async def handle_get_all_contests(callback_query: CallbackQuery):
    async with sessionmanager.session() as session:
        kb = await build_all_contests_kb(session=session)
        await callback_query.message.edit_text("🗓Все конкурсы", reply_markup=kb)


@router.callback_query(CompleteContestCbData.filter())
async def handle_delete_contest_callback(
    callback_query: CallbackQuery,
    callback_data: CompleteContestCbData
):
    async with sessionmanager.session() as session:
        contest = await get_contest_by_id(session=session, contest_id=callback_data.contest_id)
        await complete_contest_service(session=session, contest=contest)
        await callback_query.answer(
            text=f"Конкурс завершён"
        )

