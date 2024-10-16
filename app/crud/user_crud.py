from .base_crud import CRUDBase

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User, RoleEnum


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
            select(self.model).where(self.model.tg_id == tg_id)
        )

        return user.scalars().first()

    async def get_role_by_tg_id(
        self, tg_id: int, session: AsyncSession
    ) -> User:
        """Получаем роль пользователя по его tg_id."""

        result = await session.execute(
            select(self.model.role).where(self.model.tg_id == tg_id)
        )

        return result.scalar()

    async def get_manager_list(self, session: AsyncSession) -> list[User]:
        """Получить список менеджеров."""
        manager_list = await session.execute(
            select(self.model).where(self.model.role == RoleEnum.MANAGER)
        )
        return manager_list.scalars().all()

    async def promote_to_manager(
        self, user: User, name: str, session: AsyncSession
    ):
        """Назначить пользователя менеджером."""
        setattr(user, "role", RoleEnum.MANAGER)
        setattr(user, "name", name)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    async def demote_to_user(self, user: User, session: AsyncSession):
        """Снять с пользователя роль менеджера."""
        setattr(user, "role", RoleEnum.USER)
        session.add(user)
        await session.commit()
        await session.refresh(user)


user_crud = UserCRUD(User)
