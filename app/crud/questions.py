from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Info

from sqlalchemy import select


async def get_question_by_title(
    question_type: str, session: AsyncSession
) -> list[Info]:
    """Получаем все вопросы по категории."""

    result = await session.execute(
        select(Info).where(Info.question_type == question_type)
    )

    return result.scalars().all()


async def get_question_by_id(
        question_id: int, session: AsyncSession
) -> Info | None:
    """Получить вопрос по его ID."""

    result = await session.execute(
        select(Info).where(Info.id == int(question_id))
    )

    return result.scalar_one_or_none()
