import os
import asyncio
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# class YouTubeUploadService:
#     def __init__(self, auth_service):
#         self.auth_service = auth_service

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
                'categoryId': video_data.get('category_id', '22')  # People & Blogs
            },
            'status': {
                'privacyStatus': video_data.get('privacy_status', 'public'),
                'selfDeclaredMadeForKids': False
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

    # def validate_video_file(self, file_path: str) -> bool:
    #     """Валидация видеофайла"""
    #     if not os.path.exists(file_path):
    #         return False
    #
    #     # Проверка размера (макс. 256GB для YouTube)
    #     file_size = os.path.getsize(file_path)
    #     if file_size > 256 * 1024 * 1024 * 1024:
    #         return False
    #
    #     # Проверка расширения
    #     valid_extensions = {'.mp4', '.mov', '.avi', '.wmv', '.flv', '.webm', '.mkv'}
    #     return Path(file_path).suffix.lower() in valid_extensions
    #
    # def generate_thumbnail_path(self, video_path: str) -> str:
    #     """Генерация пути для thumbnail"""
    #     video_dir = os.path.dirname(video_path)
    #     video_name = os.path.splitext(os.path.basename(video_path))[0]
    #     return os.path.join(video_dir, f"{video_name}_thumbnail.jpg")
    #
    # async def set_thumbnail(self, video_id: str, thumbnail_path: str, credentials) -> bool:
    #     """Установка thumbnail для видео"""
    #     try:
    #         if not os.path.exists(thumbnail_path):
    #             return False
    #
    #         youtube = build('youtube', 'v3', credentials=credentials)
    #         media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
    #
    #         youtube.thumbnails().set(
    #             videoId=video_id,
    #             media_body=media
    #         ).execute()
    #
    #         logger.info(f"Thumbnail set for video {video_id}")
    #         return True
    #
    #     except Exception as e:
    #         logger.error(f"Failed to set thumbnail: {e}")
    #         return False