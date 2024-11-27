from testredis import broker


async def test():
    await broker.connect("redis://localhost:6379")
    await broker.publish("SOME MESSAGE", channel="test")


import asyncio
asyncio.run(test())
