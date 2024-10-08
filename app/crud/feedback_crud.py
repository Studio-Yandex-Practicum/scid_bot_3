from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .base_crud import CRUDBase
from models.models import Feedback


class FeedbackCRUD(CRUDBase):
    async def get_new_feedbacks(
        self,
        session: AsyncSession,
    ):
        """Получить список пользователей ожидающих обратного звонка."""
        users_to_callback = await session.execute(
            select(self.model)
            .where(self.model.unread)
            .order_by(desc(self.model.feedback_date))
        )
        return users_to_callback.scalars().all()

    async def mark_as_read(self, feedback: Feedback, session: AsyncSession):
        """Открыть заявку на обратный звонок."""
        setattr(feedback, "unread", False)
        session.add(feedback)
        await session.commit()
        await session.refresh(feedback)
        return feedback

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

    async def get(self, feedback_id: int, session: AsyncSession):
        """Получить объект отзыва вместе с его автором"""
        feedback_with_user = await session.execute(
            select(Feedback)
            .options(joinedload(Feedback.author))
            .where(Feedback.id == feedback_id)
        )
        return feedback_with_user.scalar_one()


feedback_crud = FeedbackCRUD(Feedback)
