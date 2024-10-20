from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base_crud import CRUDBase

from .base_manager import BaseAdminManager
from admin.keyboards.keyboards import (
    get_inline_confirmation,
    get_inline_keyboard,
)


class DeleteState(StatesGroup):
    """Класс состояний для удаления."""

    select = State()
    confirm = State()


class DeleteManager(BaseAdminManager):
    """
    Менеджер для удаления объектов из базы данных.

    Этот класс предоставляет функциональность для получения списка объектов,
    выбора объекта для удаления, подтверждения удаления и выполнения операции удаления.
    Он взаимодействует с базой данных через CRUD-операции и управляет состоянием
    пользователя в процессе удаления.

    Attributes:
        model_crud (CRUDBase): Объект для выполнения операций CRUD с моделью.
        back_option (str): Данные для возврата в меню.
        staes_group (StaesGroup): Набор машинных состояний


    Methods:
        get_all_model_names(session: AsyncSession) -> list[str]:
            Получает список названий объектов из таблицы БД.

        select_obj_to_delete(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
            Запрашивает у пользователя, какой объект он хочет удалить, и отображает список объектов.

        confirm_delete(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
            Подтверждает выбор объекта для удаления и запрашивает подтверждение от пользователя.

        delete_obj(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
            Удаляет выбранный объект из базы данных и сбрасывает состояние.
    """

    def __init__(
        self,
        model_crud: CRUDBase,
        back_option: str,
        states_group: StatesGroup = DeleteState(),
    ) -> None:
        super().__init__(model_crud, back_option, states_group)

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
        """Выбрать объкт для удаления."""
        obj_list_by_name = await self.get_all_model_names(session)
        await callback.message.edit_text(
            "Какие данные удалить?",
            reply_markup=await get_inline_keyboard(
                obj_list_by_name, previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.select)

    async def confirm_delete(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        """Подтвердить выбор объекта для удаления."""
        self.obj_to_delete = await self.model_crud.get_by_string(
            callback.data, session
        )
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить эти данные?\n\n {self.obj_to_delete.name}",
            reply_markup=await get_inline_confirmation(
                cancel_option=self.back_option
            ),
        ),
        await state.set_state(self.states_group.confirm)

    async def delete_obj(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        """Удалить объект из БД."""
        try:
            await self.model_crud.remove(self.obj_to_delete, session)
            await callback.message.edit_text(
                "Данные удалены!",
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
        except Exception as e:
            await callback.message.answer(f"Произошла ошибка: {e}")
