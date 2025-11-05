from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
from db.engine import get_db
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import redis
from db.handler.get import get_credentials_by_channel_id

router = APIRouter(prefix="/parser", tags=["parser"])

@router.get("/search")
async def search(query: str):
    return {"message": "Hello, World!"}

@router.get("/channel")
async def channel(channel_id: str, account_id: UUID, db: AsyncSession = Depends(get_db)):
    credentials_json = redis.get(f"credentials:{account_id}")

    if credentials_json is None:
        async with db() as session:
            credentials_json = await get_credentials_by_channel_id(account_id, session)

    credentials_dict = json.loads(credentials_json)
    credentials = Credentials.from_authorized_user_info(credentials_dict)

    youtube = build('youtube', 'v3', credentials=credentials)

    response = youtube.channels().list(
        part="snippet,contentDetails,statistics,status",
        forHandle=channel_id
    ).execute()

    return response
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
    #     id=channel_id
    # ).execute()

    # uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # # 2. Получаем все видео
    # videos = []
    # next_page_token = None

    # while True:
    #     playlist_response = youtube.playlistItems().list(
    #         part="snippet,contentDetails",
    #         playlistId=uploads_playlist_id,
    #         maxResults=50,
    #         pageToken=next_page_token
    #     ).execute()

    #     videos.extend(playlist_response["items"])
    #     next_page_token = playlist_response.get("nextPageToken")
    #     if not next_page_token:
    #         break

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
