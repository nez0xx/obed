import asyncio
import logging

from aiogram import Dispatcher, Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.handlers import router
from app.middlewares.apschedmiddleware import SchedulerMiddleware
from app.service import complete_contests_task
from app.settings import settings
from app.callback_handlers import router as callback_router


async def main():
    bot = Bot(token=settings.BOT_TOKEN)

    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(callback_router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()
    scheduler.add_job(complete_contests_task, trigger="interval", seconds=20, kwargs={"bot": bot})

    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


asyncio.run(main())
