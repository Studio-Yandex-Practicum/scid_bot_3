from aiogram.filters import Filter
from aiogram import Bot, types
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_crud import user_crud
from models.models import RoleEnum


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class IsManagerOrAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(
        self, message: types.Message, bot: Bot, session: AsyncSession
    ) -> bool:
        user_role = await user_crud.get_role_by_tg_id(
            message.from_user.id, session
        )
        return user_role in {RoleEnum.ADMIN, RoleEnum.MANAGER}


class IsAdminOnly(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(
        self, message: types.Message, bot: Bot, session: AsyncSession
    ) -> bool:
        user_role = await user_crud.get_role_by_tg_id(
            message.from_user.id, session
        )
        return user_role == RoleEnum.ADMIN
