from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import CRUDBase
from models.models import ProductCategory


class ProductCRUD(CRUDBase):
    async def get_last_added_product(
            self, session: AsyncSession
    ) -> ProductCategory:
        """Получить последний созданный продукт."""

        last_product = await session.execute(
            select(self.model).order_by(-self.model.id)
        )
        return last_product.scalars().first()

    async def get_by_product_name(
        self,
        product_name: str,
        session: AsyncSession,
    ) -> ProductCategory:
        """Получить объект модели по тексту названия."""

        product = await session.execute(
            select(self.model).where(self.model.name == product_name)
        )
        return product.scalars().first()


product_crud = ProductCRUD(ProductCategory)
