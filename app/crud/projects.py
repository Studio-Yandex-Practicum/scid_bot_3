from core.db import get_async_session
from models.models import (
    CheckCompanyPortfolio, ProductCategory,
    CategoryType
)
from sqlalchemy import select


async def get_all_prtfolio_projects(
        object_model: CheckCompanyPortfolio | ProductCategory
) -> list[CheckCompanyPortfolio | ProductCategory]:
    """Получение всех проектов-портфолио или продуктов и услуг."""

    async with get_async_session() as session:
        result = await session.execute(select(object_model))

        return result.scalars().all()


async def response_text_by_id(id: int) -> str:
    """Возвращает ответ на выбранную категорию."""

    async with get_async_session() as session:

        result = await session.execute(
            select(ProductCategory.response).where(ProductCategory.id == id)
        )

        return result.scalar()


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
