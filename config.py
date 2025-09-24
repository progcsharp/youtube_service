import asyncio
import os
import json
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from redis import Redis, StrictRedis

load_dotenv()

CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "client_secret.json")
SCOPES = json.loads(os.getenv("SCOPES", '["https://www.googleapis.com/auth/youtube.upload"]'))
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")

if not os.path.exists(CLIENT_SECRETS_FILE):
    raise RuntimeError(f"Client secrets file not found: {CLIENT_SECRETS_FILE}")


flow = Flow.from_client_secrets_file(
    client_secrets_file=CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_CREDENTIALS_TTL = int(os.getenv("REDIS_CREDENTIALS_TTL", 604800))

redis_broker = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

redis = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True  # Автоматически декодировать строки
        )


def get_flow():
    """Возвращает объект Flow."""
    return flow


async def close_redis():
    """Закрывает соединение с Redis."""
    if redis:
        redis.close()

