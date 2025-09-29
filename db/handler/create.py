from typing import Dict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models import Channel, Statistic, Post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException


# async def create_question(question_data: QuestionCreate, session: AsyncSession) -> Question:
#     question = Question(text=question_data.text)
#     try:
#         session.add(question)
#         await session.commit()
#         await session.refresh(question)
#
#         query = select(Question).options(selectinload(Question.answers)).where(Question.id == question.id)
#         result = await session.execute(query)
#         question_with_answers = result.scalar_one()
#
#     except SQLAlchemyError as e:
#         await session.rollback()
#         raise HTTPException(status_code=500, detail="Database error")
#     return question_with_answers


async def create_channel(channel_data: Dict, session: AsyncSession) -> Channel:
    channel = Channel(**channel_data)
    try:
        session.add(channel)
        await session.commit()
        await session.refresh(channel)
        query = select(Channel).where(Channel.account_id == channel.account_id)
        result = await session.execute(query)
        new_channel = result.scalar_one_or_none()
        return new_channel
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


async def create_statistic_to_video(statistic_data: Dict, session: AsyncSession):
    statistic = Statistic(**statistic_data)
    try:
        session.add(statistic)
        await session.commit()
        await session.refresh(statistic)
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


async def create_post(video_data: Dict, session: AsyncSession):
    post = Post(**video_data)
    try:
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")








