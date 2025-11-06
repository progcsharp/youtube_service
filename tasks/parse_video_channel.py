import json
import isodate
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
from config import redis
from db.handler.get import get_credentials_by_channel_id
from db.handler.create import create_video
from uuid import UUID
import uuid
from datetime import datetime


async def parse_video_channel(platform_channel_id: str, channel_id: str, account_id: UUID, session: AsyncSession):
    credentials_json = redis.get(f"credentials:{str(account_id)}")
    if credentials_json is None:
        credentials_json = await get_credentials_by_channel_id(str(account_id), session)
    credentials = Credentials.from_authorized_user_info(json.loads(credentials_json))
    youtube = build('youtube', 'v3', credentials=credentials)
    response = youtube.channels().list(
        part="snippet,contentDetails,statistics,status",
        id=platform_channel_id
    ).execute()
    

    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos = []
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        videos.extend(playlist_response["items"])
        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    for item in videos:
        video_id = item["contentDetails"]["videoId"]
        video_response = youtube.videos().list(
            part="snippet,statistics,contentDetails,status,player,recordingDetails,liveStreamingDetails,topicDetails",
            id=video_id
        ).execute()
        item["statistics"] = video_response["items"][0]["statistics"]
        item["contentDetails"] = video_response["items"][0]["contentDetails"]
        item["status"] = video_response["items"][0]["status"]
        item["snippet"] = video_response["items"][0]["snippet"]
        item["player"] = video_response["items"][0]["player"]
        duration = video_response["items"][0]["contentDetails"]["duration"]
        duration_timedelta = isodate.parse_duration(duration)
        duration_seconds = int(duration_timedelta.total_seconds())

        video_type = "long" if duration_seconds > 60 else "short"
        
        video = {
            "type": video_type,   
            "video_id": str(uuid.uuid4()),
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "youtube_video_id": video_id,
            "count_views": int(item.get("statistics", {}).get("viewCount", 0)),
            "count_likes": int(item.get("statistics", {}).get("likeCount", 0)),
            "count_favorites": int(item.get("statistics", {}).get("favoriteCount", 0)),
            "count_comments": int(item.get("statistics", {}).get("commentCount", 0)),
            "youtube_channel_id": channel_id,
            "published_at": datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00"))
        }

        await create_video(video, session)

