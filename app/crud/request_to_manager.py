from core.db import get_async_session
from models.models import (
    ContactManager, CheckCompanyPortfolio, User, ProductCategory
)
from sqlalchemy import select


async def create_request_to_manager(
        user_data: dict
) -> ContactManager:
    """Создание заявки на связь с менеджером."""

    async with get_async_session() as session:
        data_to_db = ContactManager(**user_data)

        session.add(data_to_db)
        await session.commit()
        await session.refresh(data_to_db)

        return data_to_db


async def get_all_prtfolio_projects(
        object_model: CheckCompanyPortfolio | ProductCategory
) -> list[CheckCompanyPortfolio | ProductCategory]:
    """Получение всех проектов-портфолио."""

    async with get_async_session() as session:
        result = await session.execute(select(object_model))

        return result.scalars().all()


async def create_user_id(tg_id: int) -> User:
    """Запись tg_id в таблицу user."""

    async with get_async_session() as session:

        data_to_db = User(tg_id=tg_id)

        session.add(data_to_db)
        await session.commit()
        await session.refresh(data_to_db)

        return data_to_db


async def get_role_by_tg_id(tg_id: int) -> User:
    """Получаем роль пользователя по его tg_id."""

    async with get_async_session() as session:

        result = await session.execute(
            select(User.role).where(User.tg_id == tg_id)
        )

        role = result.scalar()

        return role
