import asyncio

from consumer_class.redis_consumer import RedisConsumer
from cunsumer_func.upload_video import message_processing


async def main():
    redis_broker = RedisConsumer(
        host = "redis", port = 6379, db = 0, channel = "upload_video"
    )

    try:
        await redis_broker.start_consuming(message_processing)
    except KeyboardInterrupt:
        await redis_broker.stop()


if __name__ == "__main__":
    asyncio.run(main())