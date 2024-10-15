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

    async def bulk_create(
        self,
        objs_in: list,
        session: AsyncSession,
    ):
        db_objs = [self.model(**obj) for obj in objs_in]
        session.add_all(db_objs)
        await session.commit()
        return db_objs


feedback_crud = FeedbackCRUD(Feedback)
