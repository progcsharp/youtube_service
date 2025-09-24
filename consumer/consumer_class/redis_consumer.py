from typing import Callable

import redis
from loguru import logger


class RedisConsumer:
    def __init__(self, host: str, port: int, db: int, channel: str, password: str = None):
        self.host = host
        self.port = port
        self.db = db
        self.channel = channel
        self.redis_broker = None
        self.pubsub = None
        self.is_running = None

    async def connect(self):
        self.redis_broker = redis.StrictRedis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        self.pubsub = self.redis_broker.pubsub()
        self.pubsub.subscribe(self.channel)
        logger.info(f"Подключен к каналу {self.channel}")

    async def start_consuming(self, callback: Callable):

        if not self.redis_broker:
            await self.connect()

        self.is_running = True

        for message in self.pubsub.listen():
            if not self.is_running:
                break

            if message["type"] != "message":
                continue
            # try:
            logger.info(f"Получено сообщение {message['data']} в канале {self.channel}")

            data = message['data']

            await callback(data)
            logger.info(f"Сообщение {message['data']} обработано в канале {self.channel}")
            # except Exception as e:
            #     logger.error(e)

    async def stop(self):
        self.is_running = False
        if self.pubsub:
            self.pubsub.close()
        logger.info(f"Подключение к каналу {self.channel} закрыто")



