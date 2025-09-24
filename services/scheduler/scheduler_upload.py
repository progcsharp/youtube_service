import asyncio
import datetime
from typing import Dict, Any, Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from loguru import logger

from services.youtube.upload_service import upload_video


class VideoUploadScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()
        logger.info("Планировщик запущен")

    def shutdown(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик остановлен")

    async def schedule_upload(self, video_data: Dict[str, Any], credentials, scheduled_time: datetime.datetime) -> str:
        """Запланировать загрузку и вернуть ID задачи"""
        job_id = f"upload_{video_data['title']}_{scheduled_time.timestamp()}"

        self.scheduler.add_job(
            self._execute_upload,
            'date',
            run_date=scheduled_time,
            args=[video_data, credentials],
            id=job_id,
            misfire_grace_time=300  # 5 минут допуска на опоздание
        )

        logger.info(f"Загрузка запланирована на {scheduled_time} (ID: {job_id})")
        return job_id

    async def _execute_upload(self, video_data: Dict[str, Any], credentials):
        """Выполнить загрузку (вызывается планировщиком)"""
        try:
            logger.info(f"Запланированная загрузка начата")
            result = await upload_video(video_data, credentials)
            logger.info(f"Запланированная загрузка выполнена: {result['id']}")
            return result
        except Exception as e:
            logger.error(f"Ошибка запланированной загрузки: {e}")
            raise

    def cancel_scheduled_upload(self, job_id: str):
        """Отменить запланированную загрузку"""
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Загрузка отменена: {job_id}")


scheduler = VideoUploadScheduler()
