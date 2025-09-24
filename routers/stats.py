import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from config import redis, REDIS_CREDENTIALS_TTL
from db.engine import get_db
from db.handler.get import get_credentials_by_channel_id, get_latest_stats

router = APIRouter(prefix="/stats", tags=["answers"])


@router.get("/<channel_id>/<video_id>")
async def get_stats_video(channel_id, video_id, db: AsyncSession = Depends(get_db)):
    credentials_json = redis.get(f"credentials:{channel_id}")

    if credentials_json is None:
        async with db() as session:
            credentials_json = await get_credentials_by_channel_id(channel_id, session)

    credentials_dict = json.loads(credentials_json)
    credentials = Credentials.from_authorized_user_info(credentials_dict)

    redis.setex(f"credentials:{channel_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())

    youtube = build('youtube', 'v3', credentials=credentials)

    print(credentials.expiry)

    request = youtube.videos().list(
        part='snippet,statistics,contentDetails,status,player,recordingDetails,liveStreamingDetails,topicDetails',
        id=video_id
    )

    response = request.execute()
    print(credentials.expiry)
    statistic_object = {
        "stats_id": str(uuid.uuid4()),
        "post_id": str(uuid.uuid4()),  # нужно заменить на реальный post_id
        "capture_date": datetime.now(),
        "view_count": int(response["items"][0]["statistics"]["viewCount"]),
        "like_count": int(response["items"][0]["statistics"]["likeCount"]),
        "favorite_count": int(response["items"][0]["statistics"]["favoriteCount"]),
        "comment_count": int(response["items"][0]["statistics"]["commentCount"])
    }
    return statistic_object


@router.get("/<user_id>")
async def get_stats(user_id, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        stats = await get_latest_stats(user_id, session)
        redis.setex(f"stats:{user_id}", 3600, json.dumps(stats))
    return stats

