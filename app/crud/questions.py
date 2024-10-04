from core.db import get_async_session
from models.models import Info

from sqlalchemy import select


async def get_question_by_title(question_type) -> list[Info]:
    """Получаем все вопросы по категории."""

    async with get_async_session() as session:

        result = await session.execute(
            select(Info).where(Info.question_type == question_type)
        )

        return result.scalars().all()


async def get_question_by_id(question_id: int) -> Info | None:
    """Получить вопрос по его ID."""

    async with get_async_session() as session:

        result = await session.execute(
            select(Info).where(Info.id == int(question_id))
        )

        return result.scalar_one_or_none()
