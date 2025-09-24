import asyncio

from consumer_class.redis_consumer import RedisConsumer
from cunsumer_func.save_video import save_video_post


async def main():
    redis_broker = RedisConsumer(
        host = "localhost", port = 6379, db = 0, channel = "save_video"
    )

    try:
        await redis_broker.start_consuming(save_video_post)
    except KeyboardInterrupt:
        await redis_broker.stop()


if __name__ == "__main__":
    asyncio.run(main())
