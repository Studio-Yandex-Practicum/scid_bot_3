from app.admin.keyboards.keyboards import (
    get_inline_keyboard,
    InlineKeyboardManager,
)
from app.crud.base_crud import CRUDBase
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Info


class DeleteState(StatesGroup):
    """Класс состояний для удаления."""

    select = State()
    confirm = State()


class DeleteManager:
    """
    Менеджер для удаления объектов из базы данных.

    Этот класс предоставляет методы для удаления объектов из
    базы данных, используя заданную модель CRUD.

    Attributes:
        model_crud (CRUDBase): Модель, предоставляющая методы для 
        работы с объектами в БД.

        keyboard (InlineKeyboardManager): Менеджер клавиатуры для 
        взаимодействия с пользователем.

    Methods:
        delete_object(object_id: int) -> bool:
            Удаляет объект с заданным идентификатором из базы данных.
            Возвращает True, если удаление прошло успешно, иначе False.
        
        confirm_deletion(object_id: int) -> None:
            Запрашивает подтверждение у пользователя перед удалением объекта.
    """

    def __init__(
        self,
        model_crud: CRUDBase,
        keyboard: InlineKeyboardManager,
    ) -> None:
        self.model_crud = model_crud
        self.keyboard = keyboard

    async def get_all_model_names(self, session: AsyncSession) -> list[str]:
        """Получить список названий объектов из таблицы БД."""
        models = await self.model_crud.get_multi(session)
        return [model.name for model in models]

    async def select_obj_to_delete(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        obj_list_by_name = await self.get_all_model_names(session)
        await callback.message.edit_text(
            "Какой объект удалить?",
            reply_markup=await self.keyboard.add_extra_buttons(
                obj_list_by_name
            ),
        )
        await state.set_state(DeleteState.select)

    async def confirm_delete(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
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
            reply_markup=await InlineKeyboardManager.get_inline_confirmation(
                cancel_option=self.keyboard.previous_menu
            ),
        ),
        await state.set_state(DeleteState.confirm)

    async def delete_obj(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        """Удалить объект из БД."""
        await self.model_crud.remove(self.obj_to_delete, session)
        await callback.message.edit_text(
            "Данные удалены!",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.previous_menu
            ),
        )
        await state.clear()
