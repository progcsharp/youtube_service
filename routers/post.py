from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from db.handler.get import get_post_by_channel_id, get_post_by_post_id

router = APIRouter(prefix="/post", tags=["post"])


@router.get("/all/<channel_id>")
async def get_all_post_channel(channel_id,  db: AsyncSession = Depends(get_db)):
    async with db() as session:
        post = await get_post_by_channel_id(channel_id, session)
    return post


@router.get("/<post_id>")
async def get_all_post_channel(post_id: UUID,  db: AsyncSession = Depends(get_db)):
    async with db() as session:
        post = await get_post_by_post_id(post_id, session)
    return post

