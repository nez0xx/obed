from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from pyrogram import Client


class UserbotMiddleware(BaseMiddleware):
    def __init__(self, userbot: Client):
        self.userbot = userbot

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["userbot"] = self.userbot
        return await handler(event, data)
