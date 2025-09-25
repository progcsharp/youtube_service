import asyncio

from consumer_class.redis_consumer import RedisConsumer
from cunsumer_func.download_video import download_file


async def main():
    redis_broker = RedisConsumer(
        host = "redis", port = 6379, db = 0, channel = "download_video"
    )

    try:
        await redis_broker.start_consuming(download_file)
    except KeyboardInterrupt:
        await redis_broker.stop()


if __name__ == "__main__":
    asyncio.run(main())