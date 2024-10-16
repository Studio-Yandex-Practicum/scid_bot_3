from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import CRUDBase
from models.models import Info


class InfoCRUD(CRUDBase):
    async def get_by_string(
        self,
        question_text: str,
        session: AsyncSession,
    ) -> Info:
        """Получить объект модели вопроса по тексту вопроса."""

        db_obj = await session.execute(
            select(self.model).where(self.model.question == question_text)
        )
        return db_obj.scalars().first()

    async def get_all_questions_by_type(
        self,
        question_type: str,
        session: AsyncSession,
    ) -> list[Info]:
        """Получить список всех вопросов в категории."""

        obj_list = await session.execute(
            select(self.model).where(self.model.question_type == question_type)
        )
        return obj_list.scalars().all()


info_crud = InfoCRUD(Info)
