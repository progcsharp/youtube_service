from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db import make_session
from db.models import Channel, Post, YoutubeChannel, Subscription, Video
from fastapi import HTTPException


async def check_youtube_channel(youtube_id: str, session: AsyncSession) -> Channel:
    query = select(Channel).where(Channel.platform_user_id == youtube_id)
    print(query)
    result = await session.execute(query)
    youtube = result.scalar_one_or_none()

    if youtube:
        return youtube
    return youtube


async def get_credentials_by_channel_id(channel_id: UUID, session: AsyncSession):
    query = select(Channel.credentials).where(Channel.account_id == channel_id)
    result = await session.execute(query)
    channel = result.scalar_one_or_none()
    print(channel, channel_id)

    return channel


async def get_post_youtube_id(session: AsyncSession):
    query = select(Post.youtube_video_id, Post.channel_id, Post.post_id)
    result = await session.execute(query)
    list_youtube_video_id = result.all()
    return list_youtube_video_id


async def get_latest_stats(user_id: UUID, session: AsyncSession):
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
WHERE c.user_id = :user_id;
    """)

    result = await session.execute(query, {"user_id": str(user_id)})
    return result.mappings().all()


async def get_channel_by_user_id(user_id: UUID, session: AsyncSession):
    query = select(Channel).where(Channel.user_id == user_id)
    result = await session.execute(query)
    channel = result.scalars().all()

    return channel


async def get_channel_by_channel_id(account_id: UUID, session: AsyncSession):
    query = select(Channel).where(Channel.account_id == account_id)
    result = await session.execute(query)
    channel = result.scalar_one_or_none()

    return channel


async def get_post_by_channel_id(channel_id: UUID, session: AsyncSession):
    query = select(Post).where(Post.channel_id == channel_id)
    result = await session.execute(query)
    post = result.scalars().all()

    return post


async def get_post_by_post_id(post_id: UUID, session: AsyncSession):
    query = select(Post).where(Post.post_id == post_id)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    return post


async def get_youtube_channel_by_channel_id(channel_id: UUID, limit: int, type: str, session: AsyncSession):
    query = select(YoutubeChannel).where(YoutubeChannel.youtube_channel_id == channel_id).options(selectinload(YoutubeChannel.videos))
    result = await session.execute(query)
    youtube_channel = result.scalar_one_or_none()

    if not youtube_channel:
        raise HTTPException(status_code=404, detail="Youtube channel not found")

    youtube_channel.videos = sorted(
        youtube_channel.videos,
        key=lambda v: v.published_at,
        reverse=True
    )

    if type:
        youtube_channel.videos = [video for video in youtube_channel.videos if video.type == type]

    if limit:
        youtube_channel.videos = youtube_channel.videos[:limit]
    return youtube_channel


async def get_channels_by_user_id(user_id: UUID, limit: int, type: str, session: AsyncSession):
    query = select(Subscription).where(Subscription.user_id == user_id)
    result = await session.execute(query)
    subscription = result.scalars().all()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscriptions not found")

    channels = []
    for subscription in subscription:
        channel = await get_youtube_channel_by_channel_id(subscription.youtube_channel_id, limit, type, session)
        channels.append(channel)

    return channels
