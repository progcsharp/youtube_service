from sqlalchemy import update
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from db import Channel


async def update_credentials_by_channel_id(channel_id: UUID, new_credentials, session: AsyncSession):
    query = (
        update(Channel)
        .where(Channel.account_id == channel_id)
        .values(credentials=new_credentials)
        .execution_options(synchronize_session="fetch")  # чтобы сессия знала об изменениях
    )
    await session.execute(query)
    await session.commit()