from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from db.handler.get import get_channel_by_user_id, get_channel_by_channel_id
from shemas.channel import ChannelResponse

router = APIRouter(prefix="/channel", tags=["channel"])


@router.get("/all/{user_id}", response_model=List[ChannelResponse])
async def get_all_channel(user_id: UUID, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        channel = await get_channel_by_user_id(user_id, session)
    return channel


@router.get("/{account_id}", response_model=ChannelResponse)
async def get_all_channel(account_id: UUID, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        channel = await get_channel_by_channel_id(account_id, session)
    return channel
