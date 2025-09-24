import json
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import redis, redis_broker, REDIS_CREDENTIALS_TTL
from google.oauth2.credentials import Credentials

from db.engine import get_db
from db.handler.get import get_credentials_by_channel_id
from shemas.upload import AccountsRequest

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/videos")
async def upload_files(post: AccountsRequest, db: AsyncSession = Depends(get_db)):
    list_video = []
    message = []
    for item in post.accounts:

        credentials_json = redis.get(f"credentials:{item.channel_id}")

        if credentials_json is None:
            async with db() as session:
                credentials_json = await get_credentials_by_channel_id(item.channel_id, session)

        credentials_dict = json.loads(credentials_json)
        credentials = Credentials.from_authorized_user_info(credentials_dict)

        redis.setex(f"credentials:{item.channel_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())

        if not credentials:
            raise

        for media_data in item.media:
            list_video.append(str(media_data.url))

        message.append({
            "user_id": str(item.account_id),
            "urls": list_video,
            "video_data": {
                "post_id": str(uuid.uuid4()),
                "channel_id": str(item.channel_id),
                "title": item.caption,
                "description": item.description,
                "tags": item.tags,
                "category_id": "22",
                "privacy_status": "public",
                "file_path": ""
            }
            })
        redis_broker.publish("download_video", json.dumps(message))

    return message


