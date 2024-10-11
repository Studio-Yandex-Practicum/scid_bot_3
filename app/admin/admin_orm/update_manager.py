from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.admin_orm.manager_base import BaseAdminManager, CreateUpdateState
from app.admin.keyboards.keyboards import InlineKeyboardManager
from app.const import ADMIN_CONTENT_BUTTONS
from app.crud.base_crud import CRUDBase


class UpdateState(CreateUpdateState):
    """Класс состояний для редактирования данных в БД."""

    pass


class UpdateManager(BaseAdminManager):

    async def get_all_model_names(self, session: AsyncSession) -> list[str]:
        """Получить список названий объектов из таблицы БД."""
        models = await self.model_crud.get_multi(session)
        return [model.name for model in models]

    async def select_data_to_update(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """Выбрать тип данных для модели в БД."""
        await callback.message.edit_text(
            "Выбирите данные для обновления:",
            reply_markup=await self.keyboard.add_extra_buttons(
                ["Название", "Содержание"]
            ),
        )
        await state.set_state(UpdateState.select)


