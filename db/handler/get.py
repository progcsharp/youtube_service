from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db import make_session
from db.models import Channel, Post


async def check_youtube_channel(youtube_id: str, session: AsyncSession) -> Channel:
    query = select(Channel).where(Channel.youtube_channel_id == youtube_id)
    print(query)
    result = await session.execute(query)
    youtube = result.scalar_one_or_none()

    if youtube:
        return youtube
    return youtube


async def get_credentials_by_channel_id(channel_id: UUID, session: AsyncSession):
    query = select(Channel.credentials).where(Channel.channel_id == channel_id)
    result = await session.execute(query)
    channel = result.scalar_one_or_none()
    print(channel, channel_id)

    return channel


async def get_post_youtube_id(session: AsyncSession):
    query = select(Post.youtube_video_id, Post.channel_id, Post.post_id)
    result = await session.execute(query)
    list_youtube_video_id = result.all()
    return list_youtube_video_id


async def get_latest_stats(account_id: UUID, session: AsyncSession):
    query = text("""
        SELECT 
    p.post_id,
    s.view_count as total_views,
    s.like_count as total_likes,
    s.favorite_count as total_favorites,
    s.comment_count as total_comments
FROM Post p
JOIN Channel c ON p.channel_id = c.channel_id
LEFT JOIN LATERAL (
    SELECT 
        view_count,
        like_count,
        favorite_count,
        comment_count
    FROM Statistic 
    WHERE Statistic.post_id = p.post_id 
    ORDER BY capture_date DESC 
    LIMIT 1
) AS s ON true
WHERE c.account_id = :account_id;
    """)

    result = await session.execute(query, {"account_id": str(account_id)})
    return result.mappings().all()


async def get_channel_by_user_id(user_id: UUID, session: AsyncSession):
    query = select(Channel).where(Channel.account_id == user_id)
    result = await session.execute(query)
    channel = result.scalars().all()

    return channel


async def get_channel_by_channel_id(channel_id: UUID, session: AsyncSession):
    query = select(Channel).where(Channel.channel_id == channel_id)
    result = await session.execute(query)
    channel = result.scalar_one_or_none()

    return channel



