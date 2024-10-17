from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .base_crud import CRUDBase
from models.models import User, RoleEnum


class UserCRUD(CRUDBase):
    async def get_user_by_tg_id(
        self, tg_id: int, session: AsyncSession
    ) -> User:
        """Получить пользователя по его tg_id."""

        user = await session.execute(
            select(self.model).where(self.model.tg_id == int(tg_id))
        )

        return user.scalars().first()

    async def get_role_by_tg_id(
        self, tg_id: int, session: AsyncSession
    ) -> User:
        """Получаем роль пользователя по его tg_id."""

        result = await session.execute(
            select(self.model.role).where(self.model.tg_id == int(tg_id))
        )

        return result.scalar()

    async def get_manager_list(self, session: AsyncSession) -> list[User]:
        """Получить список менеджеров и администраторов."""
        manager_list = await session.execute(
            select(self.model).where(
                or_(
                    self.model.role == RoleEnum.MANAGER,
                    self.model.role == RoleEnum.ADMIN,
                )
            )
        )
        return manager_list.scalars().all()

    async def update(
        self,
        user: User,
        new_role: str,
        session: AsyncSession,
        name: str = None,
    ):
        """
        Поменять роль для пользователя и присвоить ему имя(необязательно).
        """
        if name:
            setattr(user, "name", name)
        setattr(user, "role", new_role)
        session.add(user)
        await session.commit()
        await session.refresh(user)


user_crud = UserCRUD(User)
