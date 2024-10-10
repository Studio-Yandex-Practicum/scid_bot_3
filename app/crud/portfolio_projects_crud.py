from .base_crud import CRUDBase

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import CheckCompanyPortfolio


class PortfolioProjectsCRUD(CRUDBase):
    async def get_by_project_name(
        self,
        project_name: str,
        session: AsyncSession,
    ):
        """Получить проект портфолио по тексту названия."""
        portfolio_project = await session.execute(
            select(self.model).where(self.model.name == project_name)
        )
        return portfolio_project.scalars().first()


portfolio_crud = PortfolioProjectsCRUD(CheckCompanyPortfolio)
