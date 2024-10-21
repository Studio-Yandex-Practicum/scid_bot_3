from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from admin.keyboards.keyboards import (
    get_inline_confirmation,
    get_inline_keyboard,
)
from admin.admin_settings import ADMIN_UPDATE_BUTTONS
from crud.base_crud import CRUDBase
from crud.category_product import category_product_crud
from .create_manager import CreateManager
from .update_manager import UpdateManager
from .delete_manager import DeleteManager


class CategoryCreateState(StatesGroup):
    select = State()
    name = State()
    url = State()
    description = State()
    media = State()


class CategoryUpdateState(StatesGroup):
    select = State()
    name = State()
    url = State()
    description = State()
    media = State()


class CategoryDeleteState(StatesGroup):
    select = State()
    confirm = State()


class CreateCategoryManager(CreateManager):
    def __init__(
        self,
        back_option: str,
        model_crud: CRUDBase = category_product_crud,
        states_group: StatesGroup = CategoryCreateState(),
    ) -> None:
        super().__init__(model_crud, back_option, states_group)

    async def add_obj_name(
        self,
        product_id: int,
        callback: CallbackQuery,
        state: FSMContext,
    ):
        """
        Добавить название объекта и перейти в
        следующее машинное состояние.
        """
        await callback.message.delete()
        await state.update_data(product_id=product_id)
        await callback.message.answer(
            "Введите название:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.name)


class UpdateCategoryManager(UpdateManager):
    def __init__(
        self,
        back_option: str,
        model_crud: CRUDBase = category_product_crud,
        states_group: StatesGroup = CategoryUpdateState(),
    ) -> None:
        super().__init__(model_crud, back_option, states_group)

    async def select_obj_to_update(
        self,
        product_id: int,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        obj_list = await self.model_crud.get_category_by_product_id(
            product_id, session
        )
        obj_names = [obj.name for obj in obj_list]
        obj_ids = [obj.id for obj in obj_list]
        await callback.message.edit_text(
            "Какой объект отредактировать?",
            reply_markup=await get_inline_keyboard(
                options=obj_names,
                callback=obj_ids,
                previous_menu=self.back_option,
            ),
        )
        await state.set_state(self.states_group.select)

    async def select_data_to_update(
        self,
        callback: CallbackQuery,
        session: AsyncSession,
    ):
        """Выбрать поле редактирования для модели в БД."""
        self.obj_to_update = await self.model_crud.get(callback.data, session)
        await callback.message.edit_text(
            "Выбирите данные для обновления:",
            reply_markup=await get_inline_keyboard(
                ADMIN_UPDATE_BUTTONS, previous_menu=self.back_option
            ),
        )


class DeleteCategoryManager(DeleteManager):
    def __init__(
        self,
        back_option: str,
        model_crud: CRUDBase = category_product_crud,
        states_group: StatesGroup = CategoryDeleteState(),
    ) -> None:
        super().__init__(model_crud, back_option, states_group)

    async def select_obj_to_delete(
        self,
        product_id: int,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        obj_list = await self.model_crud.get_category_by_product_id(
            product_id, session
        )
        obj_names = [obj.name for obj in obj_list]
        obj_ids = [obj.id for obj in obj_list]
        await callback.message.edit_text(
            "Какие данные удалить?",
            reply_markup=await get_inline_keyboard(
                options=obj_names,
                callback=obj_ids,
                previous_menu=self.back_option,
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
        self.obj_to_delete = await self.model_crud.get(callback.data, session)
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить эти данные?\n\n {self.obj_to_delete.name}",
            reply_markup=await get_inline_confirmation(
                cancel_option=self.back_option
            ),
        ),
        await state.set_state(self.states_group.confirm)
