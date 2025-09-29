from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ChannelResponse(BaseModel):
    platform_user_id: str
    published_at: datetime
    last_synced_at: Optional[datetime] = None
    user_id: UUID
    country_code: Optional[str] = None
    account_id: UUID
    thumbnail_url: str
    created_at: datetime
    updated_at: datetime
    title: str
    subscriber_count: int
    etag: str
    video_count: int
    description: str
    view_count: int
    custom_url: str
    privacy_status: str

    class Config:
        from_attributes = True