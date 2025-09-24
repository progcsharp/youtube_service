from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db.models import Question, Answer
from exception.database import NotFoundedError


async def delete_question(id: int, session: AsyncSession) -> bool:
    query = select(Question).where(Question.id == id)
    result = await session.execute(query)
    question = result.scalar_one_or_none()
    if not question:
        raise NotFoundedError

    await session.execute(
        delete(Answer).where(Answer.question_id == id)
    )

    await session.delete(question)
    await session.commit()
    return True


async def delete_answer(id: int, session: AsyncSession) -> bool:
    query = select(Answer).where(Answer.id == id)
    result = await session.execute(query)
    answer = result.scalar_one_or_none()
    if not answer:
        raise NotFoundedError

    await session.delete(answer)
    await session.commit()
    return True
