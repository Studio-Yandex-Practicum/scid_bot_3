from .base_crud import CRUDBase

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import InformationAboutCompany
from settings import PORTFOLIO_DEFAULT_DATA


class AboutCRUD(CRUDBase):
    async def get_by_about_name(
        self,
        about_name: str,
        session: AsyncSession,
    ):
        """Получить объект модели по тексту названия."""
        db_obj = await session.execute(
            select(self.model).where(self.model.name == about_name)
        )
        return db_obj.scalars().first()

    async def get_portfolio(self, session: AsyncSession):
        """Получить объект в котором хранится ссылка на портфолио."""
        portfolio_obj = await session.execute(
            select(self.model).where(
                self.model.name == PORTFOLIO_DEFAULT_DATA.get("name")
            )
        )
        return portfolio_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """Получить список всех объектов модели из БД."""
        db_objs = await session.execute(
            select(self.model).where(self.model.id != 1)
        )
        return db_objs.scalars().all()


company_info_crud = AboutCRUD(InformationAboutCompany)
