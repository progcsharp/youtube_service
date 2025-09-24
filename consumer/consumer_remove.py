import asyncio

from consumer_class.redis_consumer import RedisConsumer
from cunsumer_func.remove_video import delete_file


async def main():
    redis_broker = RedisConsumer(
        host = "localhost", port = 6379, db = 0, channel = "remove_video"
    )

    try:
        await redis_broker.start_consuming(delete_file)
    except KeyboardInterrupt:
        await redis_broker.stop()


if __name__ == "__main__":
    asyncio.run(main())
