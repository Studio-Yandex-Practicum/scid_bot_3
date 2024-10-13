from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from .admin import SectionState
from crud.product_crud import product_crud
from admin.filters.filters import ChatTypeFilter, IsAdmin
from admin.admin_managers import (
    DeleteState,
    UpdateState,
    CreateState,
    CreateManager,
    UpdateManager,
    DeleteManager,
)

from admin.admin_settings import (
    ADMIN_BASE_OPTIONS,
    ADMIN_UPDATE_OPTIONS,
    MAIN_MENU_OPTIONS,
)

product_router = Router()
product_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("products")

product_create_manager = CreateManager(product_crud, PREVIOUS_MENU)
product_update_manager = UpdateManager(product_crud, PREVIOUS_MENU)
product_delete_manager = DeleteManager(product_crud, PREVIOUS_MENU)


@product_router.callback_query(
    SectionState.product, F.data == ADMIN_BASE_OPTIONS.get("create")
)
async def add_product(callback: CallbackQuery, state: FSMContext):
    """Добавить название."""
    await product_create_manager.add_obj_name(callback, state)


@product_router.message(CreateState.name, F.text)
async def add_product_description(message: Message, state: FSMContext):
    """Добавить описание."""
    await product_create_manager.add_obj_description(message, state)


@product_router.message(CreateState.description, F.text)
async def creeate_product(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Создать продкет в БД."""

    await product_create_manager.add_obj_to_db(message, state, session)


@product_router.callback_query(
    SectionState.product, F.data == ADMIN_BASE_OPTIONS.get("delete")
)
async def product_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта для удаление."""
    await product_delete_manager.select_obj_to_delete(callback, state, session)


@product_router.callback_query(DeleteState.select, F.data != PREVIOUS_MENU)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтверждение удаления."""

    await product_delete_manager.confirm_delete(callback, state, session)


@product_router.callback_query(DeleteState.confirm, F.data != PREVIOUS_MENU)
async def delete_product(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить продукт из БД."""

    await product_delete_manager.delete_obj(callback, state, session)


@product_router.callback_query(
    SectionState.product, F.data == ADMIN_BASE_OPTIONS.get("update")
)
async def product_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта для редактирования."""

    await product_update_manager.select_obj_to_update(callback, state, session)


@product_router.callback_query(
    UpdateState.select,
    and_f(
        F.data != ADMIN_UPDATE_OPTIONS.get("name"),
        F.data != ADMIN_UPDATE_OPTIONS.get("content"),
        F.data != PREVIOUS_MENU,
    ),
)
async def update_choice(callback: CallbackQuery, session: AsyncSession):
    """Выбор поля для редактирования."""

    await product_update_manager.select_data_to_update(callback, session)


@product_router.callback_query(
    UpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("name")
)
async def about_name_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое название продукта."""

    await product_update_manager.change_obj_name(callback, state)


@product_router.callback_query(
    UpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("content")
)
async def about_url_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое описание продукта."""

    await product_update_manager.change_obj_content(callback, state)


@product_router.message(
    or_f(UpdateState.name, UpdateState.description), F.text
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Внести изменения продукта в БД."""

    await product_update_manager.update_obj_in_db(message, state, session)
