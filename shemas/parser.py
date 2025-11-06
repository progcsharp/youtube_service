from pydantic import BaseModel
from uuid import UUID

class ChannelCreate(BaseModel):
    channel_handle: str
    account_id: UUID
    user_id: UUID
    