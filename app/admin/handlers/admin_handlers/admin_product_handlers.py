import logging

from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.exceptions import message_exception_handler

from .admin import SectionState
from crud import products_crud
from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.admin_managers import (
    CreateManager,
    UpdateManager,
    DeleteManager,
)

from admin.admin_settings import (
    ADMIN_BASE_OPTIONS,
    ADMIN_UPDATE_OPTIONS,
    MAIN_MENU_OPTIONS,
)

logger = logging.getLogger(__name__)


product_router = Router()
product_router.message.filter(ChatTypeFilter(["private"]), IsManagerOrAdmin())
product_router.callback_query.filter(IsManagerOrAdmin())


class ProductCreateState(StatesGroup):
    select = State()
    name = State()
    url = State()
    description = State()
    media = State()


class ProductUpdateState(StatesGroup):
    select = State()
    name = State()
    url = State()
    description = State()
    media = State()


class ProductDeleteState(StatesGroup):
    select = State()
    confirm = State()


PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("products")

product_create_manager = CreateManager(
    products_crud, PREVIOUS_MENU, ProductCreateState()
)
product_update_manager = UpdateManager(
    products_crud, PREVIOUS_MENU, ProductUpdateState()
)
product_delete_manager = DeleteManager(
    products_crud, PREVIOUS_MENU, ProductDeleteState()
)


@message_exception_handler(log_error_text="Ошибка при добавлении продукта")
@product_router.callback_query(
    SectionState.product, F.data == ADMIN_BASE_OPTIONS.get("create")
)
async def add_product(callback: CallbackQuery, state: FSMContext):
    """Добавить название."""
    await product_create_manager.add_obj_name(callback, state)
    logger.info(f"Пользователь {callback.from_user.id} добавил продукт.")


@message_exception_handler(
    log_error_text="Ошибка при добавлении описания продукта"
)
@product_router.message(ProductCreateState.name, F.text)
async def add_product_description(message: Message, state: FSMContext):
    """Добавить описание."""
    await product_create_manager.add_obj_description(message, state)
    logger.info(
        f"Пользователь {message.from_user.id} добавил описание продукта."
    )


@message_exception_handler(log_error_text="Ошибка при создании продукта в БД")
@product_router.message(ProductCreateState.description, F.text)
async def create_product(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Создать продукт в БД."""
    await product_create_manager.add_obj_to_db(message, state, session)
    logger.info(f"Пользователь {message.from_user.id} создал продукт в БД.")


@message_exception_handler(
    log_error_text="Ошибка при выборе продукта для удаления"
)
@product_router.callback_query(
    SectionState.product, F.data == ADMIN_BASE_OPTIONS.get("delete")
)
async def product_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта для удаления."""
    await product_delete_manager.select_obj_to_delete(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал продукт для удаления."
    )


@message_exception_handler(
    log_error_text="Ошибка при подтверждении удаления продукта"
)
@product_router.callback_query(
    ProductDeleteState.select, F.data != PREVIOUS_MENU
)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтверждение удаления."""
    await product_delete_manager.confirm_delete(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} подтвердил удаление продукта."
    )


@message_exception_handler(log_error_text="Ошибка при удалении продукта из БД")
@product_router.callback_query(
    ProductDeleteState.confirm, F.data != PREVIOUS_MENU
)
async def delete_product(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить продукт из БД."""
    await product_delete_manager.delete_obj(callback, state, session)
    logger.info(f"Пользователь {callback.from_user.id} удалил продукт из БД.")


@message_exception_handler(
    log_error_text="Ошибка при выборе продукта для редактирования"
)
@product_router.callback_query(
    SectionState.product, F.data == ADMIN_BASE_OPTIONS.get("update")
)
async def product_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта для редактирования."""
    await product_update_manager.select_obj_to_update(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал продукт для редактирования."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе поля для редактирования"
)
@product_router.callback_query(
    ProductUpdateState.select,
    and_f(
        F.data != ADMIN_UPDATE_OPTIONS.get("name"),
        F.data != ADMIN_UPDATE_OPTIONS.get("content"),
        F.data != PREVIOUS_MENU,
    ),
)
async def update_choice(callback: CallbackQuery, session: AsyncSession):
    """Выбор поля для редактирования."""
    await product_update_manager.select_data_to_update(callback, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал поле для редактирования."
    )


@message_exception_handler(
    log_error_text="Ошибка при вводе нового названия продукта"
)
@product_router.callback_query(
    ProductUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("name")
)
async def about_name_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое название продукта."""
    await product_update_manager.change_obj_name(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} ввел новое название продукта."
    )


@message_exception_handler(
    log_error_text="Ошибка при вводе нового описания продукта"
)
@product_router.callback_query(
    ProductUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("content")
)
async def about_url_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое описание продукта."""
    await product_update_manager.change_obj_content(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} ввел новое описание продукта."
    )


@message_exception_handler(
    log_error_text="Ошибка при внесении изменений продукта в БД"
)
@product_router.message(
    or_f(ProductUpdateState.name, ProductUpdateState.description), F.text
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Внести изменения продукта в БД."""
    await product_update_manager.update_obj_in_db(message, state, session)
    logger.info(
        f"Пользователь {message.from_user.id} внес изменения продукта в БД."
    )
