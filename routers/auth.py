import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from config import get_flow, redis, REDIS_CREDENTIALS_TTL
from db.engine import get_db
from db.handler.create import create_channel
from db.handler.get import check_youtube_channel

router = APIRouter(prefix="/auth", tags=["auth"])


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
        "account_id": str(uuid.uuid4()), # acсount_id - уникальный id аккаунта платформы в нашей системе
        "user_id": state,  # user_id - уникальный id пользователя в системе
        'title': response['items'][0]['snippet']['title'],
        'etag': response['etag'],
        'description': response['items'][0]['snippet']['description'],
        'custom_url': response['items'][0]['snippet']['customUrl'],
        'platform_user_id': response['items'][0]['id'], # platform_user_id - уникальный ключ самой платформы ютуба
        'published_at': published_at,  # Теперь это datetime объект, а не строка
        'thumbnail_url': response['items'][0]['snippet']['thumbnails']['high']['url'],
        'subscriber_count': int(response['items'][0]['statistics']['subscriberCount']),
        'video_count': int(response['items'][0]['statistics']['videoCount']),
        'view_count': int(response['items'][0]['statistics']['viewCount']),
        'privacy_status': response['items'][0]['status']['privacyStatus'],
        'credentials': credentials.to_json()
    }

    async with db() as session:
        channel = await check_youtube_channel(youtube_id, session)

        if channel:
            redis.setex(f"credentials:{channel.account_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())
            return channel

        channel = await create_channel(channel_data, session)
        redis.setex(f"credentials:{channel.account_id}", REDIS_CREDENTIALS_TTL, credentials.to_json())

        return channel

