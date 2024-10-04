from core.db import get_async_session
from models.models import User
from sqlalchemy import select


async def create_user_id(tg_id: int) -> User:
    """Запись tg_id в таблицу user."""

    async with get_async_session() as session:

        data_to_db = User(tg_id=tg_id)

        session.add(data_to_db)
        await session.commit()
        await session.refresh(data_to_db)

        return data_to_db


async def is_user_in_db(tg_id: int) -> bool:
    """Проверяем, есть ли пользователь в БД."""

    async with get_async_session() as session:

        stmt = select(User).where(User.tg_id == tg_id)

        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        return user is not None


async def get_role_by_tg_id(tg_id: int) -> User:
    """Получаем роль пользователя по его tg_id."""

    async with get_async_session() as session:

        result = await session.execute(
            select(User.role).where(User.tg_id == tg_id)
        )

        return result.scalar()
