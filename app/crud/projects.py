from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import CheckCompanyPortfolio, ProductCategory, CategoryType
from sqlalchemy import select


async def get_all_prtfolio_projects(
    object_model: CheckCompanyPortfolio | ProductCategory, session: AsyncSession
) -> list[CheckCompanyPortfolio | ProductCategory]:
    """Получение всех проектов-портфолио или продуктов и услуг."""

    result = await session.execute(select(object_model))

    return result.scalars().all()


async def response_text_by_id(id: int, session: AsyncSession) -> str:
    """Возвращает ответ на выбранную категорию."""

    result = await session.execute(
        select(ProductCategory.description).where(ProductCategory.id == id)
    )

    return result.scalar()


async def get_categories_by_name(
    product_name: str, session: AsyncSession
) -> list[CategoryType]:
    """Получить все типы по категории по его названию."""

    result = await session.execute(
        select(CategoryType)
        .join(
            ProductCategory, ProductCategory.id == CategoryType.product_id
        )
        .where(ProductCategory.name == product_name)
    )

    return result.scalars().all()


async def get_title_by_id(category_id: int, session: AsyncSession) -> str:
    """Получает название категории по ID из базы данных."""

    result = await session.execute(
        select(ProductCategory.name).where(
            ProductCategory.id == category_id
        )
    )
    category_name = result.scalar()

    return category_name
