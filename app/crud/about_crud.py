from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import CRUDBase
from models.models import InformationAboutCompany


class AboutCRUD(CRUDBase):
    async def get_by_about_name(
        self,
        about_name: str,
        session: AsyncSession,
    ) -> InformationAboutCompany:
        """Получить объект модели по тексту названия."""

        db_obj = await session.execute(
            select(self.model).where(self.model.name == about_name)
        )
        return db_obj.scalars().first()


company_info_crud = AboutCRUD(InformationAboutCompany)
