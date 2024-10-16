from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import CRUDBase
from models.models import CheckCompanyPortfolio


class PortfolioProjectsCRUD(CRUDBase):
    async def get_portfolio(
        self, session: AsyncSession
    ) -> CheckCompanyPortfolio:
        """Получить объект в котором хранится ссылка на портфолио."""

        portfolio_obj = await session.execute(
            select(self.model).where(self.model.id == 1)
        )
        return portfolio_obj.scalars().first()

    async def get_multi(
        self, session: AsyncSession
    ) -> list[CheckCompanyPortfolio]:
        """
        Список объектов.

        Получить список всех объектов модели из БД,
        кроме основного портфолио.
        """

        db_objs = await session.execute(
            select(self.model).where(self.model.id != 1)
        )
        return db_objs.scalars().all()


portfolio_crud = PortfolioProjectsCRUD(CheckCompanyPortfolio)
