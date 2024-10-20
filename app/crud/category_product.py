from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base_crud import CRUDBase
from models.models import CategoryType


class CategoryTypeCRUD(CRUDBase):
    async def get_category_by_product_id(
        self, product_id: int, session: AsyncSession
    ) -> list[CategoryType]:
        """Получить список всех вариантов продукта."""

        product_categories = await session.execute(
            select(self.model).where(self.model.product_id == int(product_id))
        )
        return product_categories.scalars().all()

    async def get_category_by_name(
        self, product_id: int, field_name: str, session: AsyncSession
    ) -> CategoryType:
        """Получить категорию по имени."""

        field = await session.execute(
            select(self.model).where(
                self.model.product_id == int(product_id),
                self.model.name == field_name,
            )
        )
        return field.scalars().first()


category_product_crud = CategoryTypeCRUD(CategoryType)
