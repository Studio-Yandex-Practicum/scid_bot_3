from app.admin.keyboards.keyboards import (
    get_inline_confirmation_keyboard,
    get_inline_keyboard,
    InlineKeyboardManager,
)
from app.crud.base_crud import CRUDBase
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Info


class DeleteStates(StatesGroup):
    """Класс состояний для удаления."""

    select = State()
    confirm = State()


class DeleteManager:
    """Менеджер для удаления объекта из БД."""

    def __init__(
        self, model_curd: CRUDBase, keyboard: InlineKeyboardManager
    ) -> None:
        self.model_crud = model_curd
        self.keyboard = keyboard

    async def get_all_model_names(self, session: AsyncSession) -> list[str]:
        """Получить список названий объектов из таблицы БД."""
        models = await self.model_crud.get_multi(session)
        return [model.name for model in models]

    async def select_obj_to_delete(
        self, callback: CallbackQuery, state: FSMContext, session: AsyncSession
    ) -> None:
        obj_list_by_name = await self.get_all_model_names(session)
        await callback.message.edit_text(
            "Какой объект удалить?",
            reply_markup=self.keyboard.add_buttons(
                obj_list_by_name
            ).create_keyboard(),
        )
        await state.set_state(DeleteStates.select)

    async def confirm_delete(
        self, callback: CallbackQuery, state: FSMContext, session: AsyncSession
    ) -> None:
        self.obj_to_delete = await self.model_crud.get_by_string(
            callback.data, session
        )
        obj_data = (
            self.obj_to_delete.question
            if isinstance(self.obj_to_delete, Info)
            else self.obj_to_delete.name
        )
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить этот вопрос?\n\n {obj_data}",
            reply_markup=await get_inline_confirmation_keyboard(
                cancel_option=self.previous_menu
            ),
        )
        await state.set_state(DeleteStates.confirm)

    async def delete_obj(
        self, callback: CallbackQuery, state: FSMContext, session: AsyncSession
    ) -> None:
        """Удалить объект из БД."""
        await self.model_crud.remove(self.obj_to_delete, session)
        await callback.message.edit_text(
            "Вопрос удален!",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.previous_menu
            ),
        )
        await state.clear()
