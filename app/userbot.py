from faststream import Logger
from pyrogram import Client, filters
from pyrogram.raw.functions.messages import GetMessageReactionsList
from pyrogram.types import Message

from app.broker_redis import broker

api_id = 29915218
api_hash = "5f42ad0e52da96b991eaf9765ae4c993"

userbot = Client("Userbot", api_id=api_id, api_hash=api_hash)


@broker.subscriber(channel="userbot-channel")
async def handle_channel(msg: int, logger: Logger):
    print("MESSAGE----------------------------")
    mess_chat = -1002212016257  # тут id нужного сообщения и чат (id / username)
    r_peer = await userbot.resolve_peer(mess_chat)  # обязательно использовать этот метод для получения правильного пира
    data = await userbot.invoke(GetMessageReactionsList(peer=r_peer, id=msg, limit=-1))
    return data["count"]


userbot.run()
