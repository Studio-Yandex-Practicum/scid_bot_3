from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Feedback


async def create_feedback(user_data: dict, session: AsyncSession) -> Feedback:
    """Создание записи с отзывом."""

    data_to_db = Feedback(
        **user_data,
        feedback_date=datetime.utcnow()
    )

    session.add(data_to_db)
    await session.commit()
    await session.refresh(data_to_db)

    return data_to_db
