from datetime import datetime

from .base_crud import CRUDBase

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User


class UserCRUD(CRUDBase):
    async def get_users_with_callback_request(
        self,
        session: AsyncSession,
    ):
        """Получить список пользователей ожидающих обратного звонка."""

        users_to_callback = await session.execute(
            select(self.model)
            .where(self.model.callback_request)
            .order_by(self.model.callback_request_date)
        )

        return users_to_callback.scalars().all()

    async def get_user_by_tg_id(self, tg_id: int, session: AsyncSession):
        """Получить пользователя по его tg_id."""

        user = await session.execute(
            select(self.model).where(self.model.telegram_id == tg_id)
        )

        return user.scalars().first()

    async def case_open(self, user: User, session: AsyncSession):
        """Открыть заявку на обратный звонок."""

        setattr(user, "callback_request", True)
        setattr(user, "callback_request_date", datetime.now())

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def close_case(self, user: User, session: AsyncSession):
        """Закрыть заявку на обратный звонок."""

        setattr(user, "callback_request", False)
        setattr(user, "case_closed_date", datetime.now())

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def bulk_create(
        self,
        objs_in: list,
        session: AsyncSession,
    ):
        db_objs = [self.model(**obj) for obj in objs_in]
        session.add_all(db_objs)
        await session.commit()
        return db_objs


user_crud = UserCRUD(User)
