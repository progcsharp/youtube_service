import json
import uuid
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from db import make_session
from db.handler.create import create_statistic_to_video
from db.handler.get import get_post_youtube_id, get_credentials_by_channel_id


async def collection_statistics():
    session = make_session()
    list_video_id = await get_post_youtube_id(session)
    # await session.close()

    # print(list_video_id)
    for video_id, channel_id, post_id in list_video_id:
        credentials_json = await get_credentials_by_channel_id(channel_id, session)

        credentials_dict = json.loads(credentials_json)
        credentials = Credentials.from_authorized_user_info(credentials_dict)

        youtube = build('youtube', 'v3', credentials=credentials)

        request = youtube.videos().list(
            part='snippet,statistics,contentDetails,status,player,recordingDetails,liveStreamingDetails,topicDetails',
            id=video_id
        )

        response = request.execute()

        statistic_data = {
            "stats_id": str(uuid.uuid4()),
            "post_id": post_id,  # нужно заменить на реальный post_id
            "capture_date": datetime.now(),
            "view_count": int(response["items"][0]["statistics"]["viewCount"]),
            "like_count": int(response["items"][0]["statistics"]["likeCount"]),
            "favorite_count": int(response["items"][0]["statistics"]["favoriteCount"]),
            "comment_count": int(response["items"][0]["statistics"]["commentCount"])
        }

        await create_statistic_to_video(statistic_data, session)

    await session.close()


