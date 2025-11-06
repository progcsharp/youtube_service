from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
from db.engine import get_db
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import redis
from db.handler.get import get_credentials_by_channel_id
from db.handler.create import create_youtube_channel
from tasks.parse_video_channel import parse_video_channel
from datetime import datetime
import uuid

router = APIRouter(prefix="/parser", tags=["parser"])

@router.get("/search")
async def search(query: str):
    return {"message": "Hello, World!"}

@router.get("/channels/<user_id>")
async def channel(user_id: UUID, limit: int = None, db: AsyncSession = Depends(get_db)):
    pass


@router.get("/channel/<channel_id>")
async def channel_get(channel_id: str, db: AsyncSession = Depends(get_db)):
    pass


@router.post("/channel")
async def channel_post(channel_handle: str, account_id: UUID, db: AsyncSession = Depends(get_db)):
    
    async with db() as session:
        credentials_json = redis.get(f"credentials:{str(account_id)}")
        if credentials_json is None:
            credentials_json = await get_credentials_by_channel_id(str(account_id), session)
        credentials = Credentials.from_authorized_user_info(json.loads(credentials_json))
        youtube = build('youtube', 'v3', credentials=credentials)
        response = youtube.channels().list(
            part="snippet,contentDetails,statistics,status",
            forHandle=channel_handle
        ).execute()

        channel_data = {
            "youtube_channel_id": uuid.uuid4(),
            "etag": response["etag"],
            "title": response["items"][0]["snippet"]["title"],
            "description": response["items"][0]["snippet"]["description"],
            "custom_url": response["items"][0]["snippet"]["customUrl"],
            "platform_channel_id": response["items"][0]["id"],
            "subscriber_count": response["items"][0]["statistics"]["subscriberCount"],
            "video_count": response["items"][0]["statistics"]["videoCount"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        # await create_youtube_channel(channel_data, session)
        return channel_data


    # credentials_json = redis.get(f"credentials:{account_id}")

    # if credentials_json is None:
    #     async with db() as session:
    #         credentials_json = await get_credentials_by_channel_id(account_id, session)

    # credentials_dict = json.loads(credentials_json)
    # credentials = Credentials.from_authorized_user_info(credentials_dict)

    # youtube = build('youtube', 'v3', credentials=credentials)

    # response = youtube.channels().list(
    #     part="snippet,contentDetails,statistics,status",
    #     id=channel_id
    # ).execute()

    # return response
    # credentials_json = redis.get(f"credentials:{account_id}")

    # if credentials_json is None:
    #     async with db() as session:
    #         credentials_json = await get_credentials_by_channel_id(account_id, session)

    # credentials_dict = json.loads(credentials_json)
    # credentials = Credentials.from_authorized_user_info(credentials_dict)
    # youtube = build('youtube', 'v3', credentials=credentials)

    # # 1. Получаем uploads playlist ID
    # channel_response = youtube.channels().list(
    #     part="contentDetails",
    #     forHandle=channel_id
    # ).execute()

    # uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # # 2. Получаем все видео
    # videos = []
    # next_page_token = None


    # playlist_response = youtube.playlistItems().list(
    #     part="snippet,contentDetails",
    #     playlistId=uploads_playlist_id,
    #     maxResults=50,
    #     pageToken=next_page_token
    # ).execute()

    # videos.extend(playlist_response["items"])
    # next_page_token = playlist_response.get("nextPageToken")


    # for item in videos:
    #     video_id = item["contentDetails"]["videoId"]
    #     video_response = youtube.videos().list(
    #         part="snippet,statistics,contentDetails,status,player,recordingDetails,liveStreamingDetails,topicDetails",
    #         id=video_id
    #     ).execute()
    #     item["statistics"] = video_response["items"][0]["statistics"]
    #     item["contentDetails"] = video_response["items"][0]["contentDetails"]
    #     item["status"] = video_response["items"][0]["status"]

    # # 3. Возвращаем только нужные поля
    # return videos
