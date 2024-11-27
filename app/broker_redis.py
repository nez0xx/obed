from faststream import FastStream
from faststream.redis import RedisBroker


broker = RedisBroker("redis://localhost:6379")
app = FastStream(broker)


