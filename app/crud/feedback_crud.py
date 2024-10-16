from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import CRUDBase
from models.models import Feedback


class FeedbackCRUD(CRUDBase):
    async def get_multi(self, session: AsyncSession):
        """Получить список всех объектов модели из БД."""
        db_objs = await session.execute(
            select(self.model).order_by(desc(self.model.feedback_date))
        )
        return db_objs.scalars().all()


feedback_crud = FeedbackCRUD(Feedback)
