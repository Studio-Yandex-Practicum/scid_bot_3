from core.db import get_async_session
from models.models import (
    ContactManager, CheckCompanyPortfolio, User, ProductCategory,
    Info, CategoryType
)
from sqlalchemy import select


async def create_request_to_manager(
        user_data: dict
) -> ContactManager:
    """Создание заявки на связь с менеджером."""

    async with get_async_session() as session:
        data_to_db = ContactManager(**user_data)
        # TODO: нужно поменять значение need_contact_with_manager на True
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


async def response_text_by_id(id: int) -> str:
    """Возвращает ответ на выбранную категорию."""

    async with get_async_session() as session:

        result = await session.execute(
            select(ProductCategory.response).where(ProductCategory.id == id)
        )

        return result.scalar()


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


async def get_categories_by_name(
    product_name: str
) -> list[CategoryType]:
    """Получить все типы по категории по его названию."""

    async with get_async_session() as session:

        result = await session.execute(
            select(CategoryType)
            .join(
                ProductCategory, ProductCategory.id == CategoryType.product_id
            )
            .where(ProductCategory.title == product_name)
        )

        return result.scalars().all()


async def get_title_by_id(category_id: int) -> str:
    """Получает название категории по ID из базы данных."""

    async with get_async_session() as session:

        result = await session.execute(
            select(ProductCategory.title).where(
                ProductCategory.id == category_id
            )
        )
        category_name = result.scalar()

        return category_name
