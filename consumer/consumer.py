from typing import Callable

from consumer.consumer_class.redis_consumer import RedisConsumer


async def consumer(processing_func: Callable, channel: str):
    redis_broker = RedisConsumer(
        host = "localhost", port = 6379, db = 0, channel = channel
    )

    try:
        await redis_broker.start_consuming(processing_func)
    except KeyboardInterrupt:
        await redis_broker.stop()
