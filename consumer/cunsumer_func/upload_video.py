import json
import os
import asyncio
import uuid
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from redis import Redis, StrictRedis

from db import make_session
from db.handler.get import get_credentials_by_channel_id

logger = logging.getLogger(__name__)


async def upload_video(video_data: Dict[str, Any], credentials) -> Optional[Dict[str, Any]]:
    """Загрузка видео на YouTube"""
    try:
        youtube = build('youtube', 'v3', credentials=credentials)

        # Подготовка тела запроса
        body = {
            'snippet': {
                'title': video_data['title'],
                'description': video_data['description'],
                'tags': video_data.get('tags', []),
                'categoryId': video_data.get('category_id', '22'),  # People & Blogs
                # Добавляем параметры для Shorts
                'isShort': True  # Это основной параметр для Shorts
            },
            'status': {
                'privacyStatus': video_data.get('privacy_status', 'public'),
                'selfDeclaredMadeForKids': False,
                # Дополнительные параметры для Shorts
                'madeForKids': False
            },
            # Добавляем специальные параметры для Shorts
            'contentDetails': {
                'duration': 'PT60S',  # Длительность до 60 секунд для Shorts
                'definition': 'sd',  # Стандартное качество
                'caption': 'false',
                'licensedContent': False,
                'projection': 'rectangular'
            }
        }

        # Загрузка медиафайла
        media = MediaFileUpload(
            video_data['file_path'],
            chunksize=1024 * 1024,
            resumable=True,
            mimetype='video/*'
        )

        # Выполнение запроса
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        # Асинхронная загрузка с прогрессом
        response = await _execute_resumable_upload(request)

        logger.info(f"Video uploaded successfully: {response['id']}")

        redis_broker = StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
        redis_broker.publish("remove_video", json.dumps({"file_path": video_data["file_path"]}))

        snippet = response['snippet']
        status = response['status']

        post_data = {
            'post_id': str(uuid.uuid4()),
            'channel_id': video_data["channel_id"],
            'title': snippet['title'],
            'description': snippet['description'],
            'youtube_video_id': response['id'],
            'tags': list(snippet['tags']),
            # 'published_at': datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').isoformat(),
            'privacy_status': status['privacyStatus'],
        }


        redis_broker.publish("save_video", json.dumps(post_data))

        return response

    except Exception as e:
        logger.error(f"Video upload failed: {e}")
        raise


async def _execute_resumable_upload(request) -> Dict[str, Any]:
    """Выполнение возобновляемой загрузки с прогрессом"""
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            await asyncio.sleep(1)  # Неблокирующая задержка
        except Exception as e:
            logger.warning(f"Upload chunk error: {e}")
            await asyncio.sleep(5)  # Пауза перед повторной попыткой

    return response


async def message_processing(data):
    data = json.loads(data)
    video_data = data["video_data"]

    redis = Redis(
            host="redis",
            port=6379,
            db=0,
            decode_responses=True  # Автоматически декодировать строки
        )

    credentials_json = redis.get(f"credentials:{data['user_id']}")

    if credentials_json is None:
        # async with db() as session:
        session = make_session()
        credentials_json = await get_credentials_by_channel_id(video_data["channel_id"], session)
        await session.close()

    credentials_dict = json.loads(credentials_json)
    credentials = Credentials.from_authorized_user_info(credentials_dict)

    await upload_video(video_data, credentials)

