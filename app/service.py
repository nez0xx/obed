from datetime import datetime
from random import choice

from aiogram import Bot
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.crud import get_user_comments_in_contest, get_contest_by_post_id, create_comment, get_user_by_id, create_user, \
    get_comments_by_contest_id, create_win, get_contest_winners, get_uncompleted_contests, get_all_contests, \
    get_all_wins, get_all_comments, get_reaction_by_user_and_comment, create_reaction, get_reactions_by_message_id, \
    get_comment_by_id, get_win_by_contest_and_user, get_contest_participants
from app.database import Comment, Contest, Reaction
from app.exceptions import Conflict
from app.database.db_helper import sessionmanager

from app.settings import settings
from app.utils import format_message


async def create_contest_service(start_dt: datetime, end_dt: datetime, post_id: int):
    session = sessionmanager.session()

    active_contest = await crud.get_contest_by_post_id(session=session, post_id=post_id)
    if active_contest:
        raise Conflict(detail="Active comments contest already exists")

    await crud.create_contest(
        session=session,
        post_id=post_id,
        start_time=start_dt,
        end_time=end_dt
    )

    await session.close()


async def create_comment_service(message_id: int, user_id: str, post_id: int, username: str | None, name: str):
    session = sessionmanager.session()

    contest = await get_contest_by_post_id(session=session, post_id=post_id)

    if contest is None:
        return
    contest_id = contest.id

    user = await get_user_by_id(session=session, user_id=user_id)

    if user is None:
        await create_user(session=session, user_id=user_id, username=username, name=name)
    else:

        user_comments = await get_user_comments_in_contest(session=session, user_id=user_id, contest_id=contest_id)
        if len(user_comments) >= 3:
            return

    await create_comment(session=session, user_id=user_id, contest_id=contest_id, message_id=message_id)
    print(f"CREATED {message_id}")
    await session.close()


async def get_most_liked_comm(comments: list[Comment]) -> int:
    max_reactions = 0
    comm_idx = 0
    for i in range(len(comments)-1):
        reactions = await count_message_reactions_service(comments[i].id)
        if reactions > max_reactions:
            max_reactions = reactions
            comm_idx = i
    return comm_idx


async def create_win_service(session: AsyncSession, contest_id: int, user_id: int, win_type: str):
    existing_win = await get_win_by_contest_and_user(session=session, contest_id=contest_id, user_id=user_id)
    if existing_win:
        return
    await create_win(session=session, contest_id=contest_id, win_type=win_type, user_id=user_id)


async def complete_contest_service(session: AsyncSession, contest: Contest, with_commit: bool = False) -> dict | None:

    comments = await get_comments_by_contest_id(session=session, contest_id=contest.id)
    participants = await get_contest_participants(session=session, contest_id=contest.id)
    
    if len(comments) < 3 or len(participants) < 3:
        stmt = update(Contest).where(Contest.id == contest.id).values(completed=True)
        await session.execute(stmt)
        if with_commit:
            await session.commit()
        else:
            await session.flush()
        return None

    most_liked_comm_idx = await get_most_liked_comm(comments)
    most_liked_comm = comments[most_liked_comm_idx]

    comm_under_previous_comm_idx = most_liked_comm_idx+1
    comm_under_previous_comm = comments[comm_under_previous_comm_idx]

    while True:
        comm = comments[comm_under_previous_comm_idx]
        if comm.user_id == most_liked_comm.user_id:
            comm_under_previous_comm_idx += 1
        else:
            comm_under_previous_comm = comments[comm_under_previous_comm_idx]
            break
    random_comm_idx = choice(
        [i for i in range(len(comments)) if i not in [most_liked_comm_idx, comm_under_previous_comm_idx]]
    )

    random_comm = comments[random_comm_idx]

    user1 = await get_user_by_id(session=session, user_id=most_liked_comm.user_id)
    user2 = await get_user_by_id(session=session, user_id=comm_under_previous_comm.user_id)
    user3 = await get_user_by_id(session=session, user_id=random_comm.user_id)

    await create_win_service(session=session, contest_id=contest.id, win_type="likes", user_id=user1.id)
    await create_win_service(session=session, contest_id=contest.id, win_type="under", user_id=user2.id)
    await create_win_service(session=session, contest_id=contest.id, win_type="random", user_id=user3.id)

    contest.completed = True
    stmt = update(Contest).where(Contest.id == contest.id).values(completed=True)
    await session.execute(stmt)
    print("SOMETHING ")
    if with_commit:
        await session.commit()
    else:
        await session.flush()

    return {
        "likes": user1,
        "under": user2,
        "random": user3
    }


async def get_contest_winners_service(contest_id: int) -> dict:
    session = sessionmanager.session()

    wins = await get_contest_winners(session=session, contest_id=contest_id)

    data = {}
    for win in wins:
        data[win.type] = win.user_relationship

    await session.close()

    return data


async def complete_contests_task(bot: Bot):
    async with sessionmanager.session() as session:
        contests = await get_uncompleted_contests(session=session)
        for contest in contests:
            winners = await complete_contest_service(contest=contest, session=session)
            if winners is not None:
                msg = format_message(winners=winners)
                await bot.send_message(chat_id=settings.CHIEF_CHAT_ID, text=msg)
        await session.commit()


async def get_statistics_service() -> dict:
    async with sessionmanager.session() as session:
        contests_count = len(await get_all_contests(session=session))
        winners_count = len(await get_all_wins(session=session))
        comments_count = len(await get_all_comments(session=session))

    return {
        "contests_count": contests_count,
        "winners_count": winners_count,
        "comments_count": comments_count
    }


async def create_reaction_service(user_id: str, message_id: int):
    async with sessionmanager.session() as session:
        comment = await get_comment_by_id(session=session, message_id=message_id)
        if comment is None:
            return

        existing_reaction = await get_reaction_by_user_and_comment(
            session=session,
            user_id=user_id,
            message_id=message_id
        )

        if existing_reaction:
            return

        await create_reaction(session=session, user_id=user_id, message_id=message_id)


async def count_message_reactions_service(message_id: int) -> int:
    async with sessionmanager.session() as session:
        reactions = await get_reactions_by_message_id(session=session, message_id=message_id)
    return len(reactions)










