from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import User, Win, Task
from app.database.db_model_contest import Contest
from app.database.db_model_comment import Comment


async def create_contest(
        session: AsyncSession,
        post_id: int,
        start_time: datetime,
        end_time: datetime,
        with_commit: bool = True
) -> Contest:
    model = Contest(
        post_id=post_id,
        start_time=start_time,
        end_time=end_time
    )

    session.add(model)
    await session.flush()
    if with_commit:
        await session.commit()

    return model


async def get_contest_by_id(session: AsyncSession, contest_id: int) -> Contest | None:
    stmt = select(Contest).where(Contest.id == contest_id)
    result = await session.execute(stmt)
    contest = result.scalar_one_or_none()
    return contest


async def get_contest_by_post_id(
        session: AsyncSession,
        post_id: int,
) -> Contest | None:
    stmt = select(Contest).where(Contest.post_id == post_id)
    result = await session.execute(stmt)
    contest = result.scalar_one_or_none()
    return contest


async def get_active_contests(session: AsyncSession) -> list[Contest]:
    now = datetime.now()

    stmt = (select(Contest)
            .where(Contest.start_time < now)
            .where(Contest.end_time > now))
    result = await session.execute(stmt)
    contests = list(result.scalars())

    return contests


async def delete_contest(session: AsyncSession, contest_id: int, with_commit: bool = True):
    stmt = delete(Contest).where(Contest.id == contest_id)
    await session.execute(stmt)
    stmt = delete(Comment).where(Comment.contest_id == contest_id)
    await session.execute(stmt)

    await session.flush()
    if with_commit:
        await session.commit()


async def create_comment(
        session: AsyncSession,
        contest_id: int,
        message_id: str,
        user_id: str,
        with_commit: bool = True,
):
    model = Comment(
        contest_id=contest_id,
        message_id=message_id,
        user_id=user_id
    )

    session.add(model)
    await session.flush()
    if with_commit:
        await session.commit()


async def get_user_comments(session: AsyncSession, user_id: str) -> list[Comment]:
    stmt = select(Comment).where(Comment.user_id == user_id)
    result = await session.execute(stmt)
    comments = list(result.scalars())
    return comments


async def get_user_comments_in_contest(session: AsyncSession, contest_id: int, user_id: str) -> list[Comment]:
    stmt = select(Comment).where(Comment.user_id == user_id).where(Comment.contest_id == contest_id)
    result = await session.execute(stmt)
    comments = result.scalars()
    return list(comments)


async def get_all_contests(session: AsyncSession, offset: int = 0, limit: int | None = None) -> list:
    stmt = select(Contest).order_by(Contest.start_time).offset(offset)
    if limit:
        stmt = stmt.limit(limit+1)
    result = await session.execute(stmt)
    contests = result.scalars()
    return list(contests)


async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(session: AsyncSession, user_id: str, username: str):
    model = User(id=user_id, username=username)
    session.add(model)
    await session.commit()
    return model


async def get_comments_by_contest_id(session: AsyncSession, contest_id: int) -> list[Comment]:
    stmt = select(Comment).where(Comment.contest_id == contest_id).order_by(Comment.message_id)
    result = await session.execute(stmt)
    comments = result.scalars()
    return list(comments)


async def create_win(session: AsyncSession, contest_id: int, win_type: str, user_id: int, with_commit: bool = False):
    model = Win(
        contest_id=contest_id,
        user_id=user_id,
        type=win_type
    )

    session.add(model)
    if with_commit:
        await session.commit()
    else:
        await session.flush()


async def get_contest_winners(session: AsyncSession, contest_id: int) -> list[Win]:
    stmt = select(Win).options(joinedload(Win.user_relationship)).where(Win.contest_id == contest_id)
    result = await session.execute(stmt)
    wins = list(result.scalars())

    return wins


async def create_task(session: AsyncSession, contest_id: int, task_id: int):
    model = Task(contest_id=contest_id, task_id=task_id)
    session.add(model)
    await session.commit()


async def get_task_by_id(session: AsyncSession, task_id: int) -> Task | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    return task


async def get_uncompleted_contests(session: AsyncSession) -> list[Contest]:
    now = datetime.now()
    stmt = select(Contest).where(Contest.completed == False).where(Contest.end_time < now)
    result = await session.execute(stmt)
    contests = result.scalars()
    return list(contests)


async def count_participicants(session: AsyncSession, contest_id: int) -> int:
    comms = await get_comments_by_contest_id(session=session, contest_id=contest_id)
    users = list(set([c.user_id for c in comms]))
    return len(users)


async def get_all_wins(session: AsyncSession) -> list[Win]:
    stmt = select(Win)
    result = await session.execute(stmt)
    wins = result.scalars()
    return list(wins)


async def get_all_comments(session: AsyncSession) -> list[Comment]:
    stmt = select(Comment)
    result = await session.execute(stmt)
    comments = result.scalars()
    return list(comments)
