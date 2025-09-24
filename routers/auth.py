import json
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as google_request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from config import get_flow, redis, REDIS_CREDENTIALS_TTL
from db.engine import get_db
from db.handler.create import create_channel
from db.handler.get import check_youtube_channel

router = APIRouter(prefix="/auth", tags=["answers"])


@router.get("/login/<user_id>")
async def login(user_id):
    try:
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=user_id
        )

        response = JSONResponse({
            "auth_url": authorization_url
        })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")


@router.get("/callback")
async def auth_callback(code: str, state: str, db: AsyncSession = Depends(get_db)):
    """Обрабатывает callback от Google"""
    # try:

    flow = get_flow()
    flow.fetch_token(code=code)

    # Сохраняем credentials
    credentials = flow.credentials
    # user_id = str(uuid.uuid4())
    # redis.setex(f"credentials:{user_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())
    # print(user_id)
    # print(credentials.expiry)

    # response = JSONResponse({
    #     "success": True,
    #     "user_id": user_id,
    #     "message": "Authentication successful"
    # })
    # response.set_cookie(key="user_id", value=user_id, httponly=True)

    youtube = build('youtube', 'v3', credentials=credentials)

    response = youtube.channels().list(
        part="snippet,contentDetails,statistics,status",
        mine=True
    ).execute()

    youtube_id = response["items"][0]["id"]

    published_at_str = response['items'][0]['snippet']['publishedAt']
    # Убираем 'Z' в конце и добавляем временную зону +00:00
    published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))

    channel_data = {
        "channel_id": str(uuid.uuid4()),
        "account_id": str(uuid.uuid4()),  # state,
        'title': response['items'][0]['snippet']['title'],
        'etag': response['etag'],
        'description': response['items'][0]['snippet']['description'],
        'custom_url': response['items'][0]['snippet']['customUrl'],
        'youtube_channel_id': response['items'][0]['id'],
        'published_at': published_at,  # Теперь это datetime объект, а не строка
        'thumbnail_url': response['items'][0]['snippet']['thumbnails']['high']['url'],
        'subscriber_count': int(response['items'][0]['statistics']['subscriberCount']),
        'video_count': int(response['items'][0]['statistics']['videoCount']),
        'view_count': int(response['items'][0]['statistics']['viewCount']),
        'privacy_status': response['items'][0]['status']['privacyStatus'],
        'credentials': credentials.to_json()
    }
    print(channel_data)

    async with db() as session:
        channel = await check_youtube_channel(youtube_id, session)

        if channel:
            redis.setex(f"credentials:{channel.channel_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())
            return channel

        channel = await create_channel(channel_data, session)
        redis.setex(f"credentials:{channel.channel_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())

        return channel

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Callback error: {str(e)}")


# @router.get("/status")
# async def auth_status(request: Request):
#     """Проверяет статус аутентификации"""
#     user_id = request.cookies.get("user_id")
#     print(user_id)
#     if user_id:
#         credentials_json = redis.get(f"credentials:{user_id}")
#         if credentials_json:
#             creds = Credentials.from_authorized_user_info(json.loads(credentials_json))
#             if not creds.valid and creds.expired and creds.refresh_token:
#                 print(f"Refreshing credentials for user_id: {user_id}")
#                 creds.refresh(google_request())
#                 redis.setex(f"credentials:{user_id}", REDIS_CREDENTIALS_TTL, creds.to_json())
#                 print(f"Stored credentials for user_id: {user_id}")
#
#             if creds:
#                 youtube = build('youtube', 'v3', credentials=creds)
#
#                 response = youtube.channels().list(
#                     part="snippet,contentDetails",
#                     mine=True
#                 ).execute()
#
#                 return {"authenticated": True, "user_id": user_id, "channels": response}
#     return {"authenticated": False}
