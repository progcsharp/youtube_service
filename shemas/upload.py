from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class MediaItem(BaseModel):
    url: HttpUrl
    media_type: str  # Можно использовать Enum если типы ограничены
    media_id: str


class PlatformSpecificData(BaseModel):
    location_id: Optional[str] = None
    description: Optional[str] = None  # Опциональное описание
    tags: Optional[List[str]] = None
    # Добавьте другие специфичные поля по необходимости


class AccountPost(BaseModel):
    user_id: UUID
    account_id: UUID
    post_id: UUID
    post_type: str  # Можно использовать Enum если типы ограничены
    caption: str
    media: List[MediaItem]
    scheduled_time: Optional[datetime] = None
    platform_specific_data: PlatformSpecificData = PlatformSpecificData()



class AccountsRequest(BaseModel):
    accounts: List[AccountPost]
