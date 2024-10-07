from .base_crud import CRUDBase

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ProductCategory


class ProductCRUD(CRUDBase):
    async def get_last_added_product(self, session: AsyncSession):
        """Получить последний созданный продукт."""
        last_product = await session.execute(
            select(self.model).order_by(-self.model.id)
        )
        return last_product.scalars().first()

    async def get_by_product_name(
        self,
        product_name: str,
        session: AsyncSession,
    ):
        """Получить объект модели по тексту названия."""
        product = await session.execute(
            select(self.model).where(self.model.title == product_name)
        )
        return product.scalars().first()


product_crud = ProductCRUD(ProductCategory)
