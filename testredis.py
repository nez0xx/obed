from faststream import FastStream
from faststream.redis import RedisBroker
import asyncio


broker = RedisBroker("redis://localhost:6379")

app = FastStream(broker)


@broker.subscriber("test")
async def base_handler(body):
    print(body)







