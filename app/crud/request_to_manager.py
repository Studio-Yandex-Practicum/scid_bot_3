from core.db import get_async_session
from models.models import ContactManager, CheckCompanyPortfolio
from sqlalchemy import select


async def create_request_to_manager(
        user_data: dict
):
    """Создание заявки на связь с менеджером."""

    async with get_async_session() as session:
        data_to_db = ContactManager(**user_data)

        session.add(data_to_db)
        await session.commit()
        await session.refresh(data_to_db)

        return data_to_db


async def get_all_prtfolio_projects():
    """Получение всех проектов-портфолио."""

    async with get_async_session() as session:
        result = await session.execute(select(CheckCompanyPortfolio))

        return result.scalars().all()
