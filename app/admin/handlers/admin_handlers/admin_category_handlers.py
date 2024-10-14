import logging

from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.handlers.admin_handlers.admin import SectionState
from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.admin_managers import (
    CreateCategoryManager,
    UpdateCategoryManager,
    DeleteCategoryManager,
    CategoryCreateState,
    CategoryUpdateState,
    CategoryDeleteState,
)
from admin.handlers.user import ProductCategory
from admin.admin_settings import (
    ADMIN_BASE_OPTIONS,
    ADMIN_CONTENT_OPTIONS,
    ADMIN_UPDATE_OPTIONS,
    MAIN_MENU_OPTIONS,
)
from admin.keyboards.keyboards import get_inline_keyboard
from bot.exceptions import message_exception_handler
from crud.category_product import category_product_crud
from crud.product_crud import product_crud

logger = logging.getLogger(__name__)

category_router = Router()
category_router.message.filter(ChatTypeFilter(["private"]), IsManagerOrAdmin())

PREVIOUS_MENU = "Назад"


category_create_manager = CreateCategoryManager(PREVIOUS_MENU)
category_update_manager = UpdateCategoryManager(PREVIOUS_MENU)
category_delete_manager = DeleteCategoryManager(PREVIOUS_MENU)


async def get_categoties_by_product_id(state: FSMContext):
    """Получить id продукта из состояния."""
    fsm_data = await state.get_data()
    return fsm_data.get("product_id")


@message_exception_handler(
    log_error_text="Ошибка при возврате к меню категорий"
)
@category_router.callback_query(
    or_f(
        State(None),
        CategoryCreateState(),
        CategoryUpdateState(),
        CategoryDeleteState(),
        SectionState.category,
    ),
    F.data == PREVIOUS_MENU,
)
async def get_back_to_category_menu(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Корутина для реализации кнопки 'Назад'."""
    fsm_data = await state.get_data()
    product = await product_crud.get(fsm_data.get("product_id"), session)
    categories = await category_product_crud.get_category_by_product_id(
        fsm_data.get("product_id"), session
    )
    categories_by_name = [category.name for category in categories]
    urls = [category.url for category in categories]
    await callback.message.edit_text(
        f"{product.description}",
        reply_markup=await get_inline_keyboard(
            categories_by_name,
            urls=urls,
            previous_menu=MAIN_MENU_OPTIONS.get("products"),
            admin_update_menu=callback.data,
        ),
    )
    await state.set_state(ProductCategory.product_id)
    logger.info(
        f"Пользователь {callback.from_user.id} вернулся в меню категорий."
    )


@message_exception_handler(
    log_error_text="Ошибка при добавлении названия категории"
)
@category_router.callback_query(
    SectionState.category, F.data == ADMIN_BASE_OPTIONS.get("create")
)
async def add_product_category_name(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Добавить название категории."""
    product_id = await get_categoties_by_product_id(state)
    await category_create_manager.add_obj_name(product_id, callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} добавил название категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе типа данных для категории"
)
@category_router.message(CategoryCreateState.name, F.text)
async def select_new_category_type(message: Message, state: FSMContext):
    """Выбрать тип данных для дополнительной информации о продукте."""
    await category_create_manager.select_data_type(message, state)
    logger.info(
        f"Пользователь {message.from_user.id} выбрал тип данных для категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при добавлении ссылки на категорию"
)
@category_router.callback_query(
    CategoryCreateState.select, F.data == ADMIN_CONTENT_OPTIONS.get("url")
)
async def add_product_category_url(callback: CallbackQuery, state: FSMContext):
    """Добавить ссылку на категорию."""
    await category_create_manager.add_obj_url_callback(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} добавил ссылку на категорию."
    )


@message_exception_handler(
    log_error_text="Ошибка при добавлении описания категории"
)
@category_router.callback_query(
    CategoryCreateState.select,
    F.data == ADMIN_CONTENT_OPTIONS.get("description"),
)
async def add_product_category_description(
    callback: CallbackQuery, state: FSMContext
):
    """Добавить текст описания категории."""
    await category_create_manager.add_obj_description_callback(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} добавил описание категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при добавлении медиа для категории"
)
@category_router.callback_query(
    CategoryCreateState.select, F.data == ADMIN_CONTENT_OPTIONS.get("media")
)
async def add_product_category_media(
    callback: CallbackQuery, state: FSMContext
):
    """Добавить картинку для категории."""
    await category_create_manager.add_obj_media_callback(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} добавил медиа для категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при создании информации для продукта в БД"
)
@category_router.message(
    or_f(
        CategoryCreateState.description,
        CategoryCreateState.url,
        CategoryCreateState.media,
    ),
    or_f(F.text, F.photo),
)
async def create_product_with_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Создать информацию для продукта в БД."""
    await category_create_manager.add_obj_to_db(message, state, session)
    logger.info(
        f"Пользователь {message.from_user.id} создал информацию для продукта в БД."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе категории для удаления"
)
@category_router.callback_query(
    SectionState.category, F.data == ADMIN_BASE_OPTIONS.get("delete")
)
async def product_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор информации на удаление."""
    product_id = await get_categoties_by_product_id(state)
    await category_delete_manager.select_obj_to_delete(
        product_id, callback, state, session
    )
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал категорию для удаления."
    )


@message_exception_handler(
    log_error_text="Ошибка при подтверждении удаления категории"
)
@category_router.callback_query(CategoryDeleteState.select, F.data)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтверждение удаления категории."""
    await category_delete_manager.confirm_delete(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} подтвердил удаление категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при удалении категории из БД"
)
@category_router.callback_query(
    CategoryDeleteState.confirm, F.data != PREVIOUS_MENU
)
async def delete_category(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить информацию о категории из БД."""
    await category_delete_manager.delete_obj(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} удалил категорию из БД."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе категории для обновления"
)
@category_router.callback_query(
    SectionState.category, F.data == ADMIN_BASE_OPTIONS.get("update")
)
async def category_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор информации для редактирования категории."""
    product_id = await get_categoties_by_product_id(state)
    await category_update_manager.select_obj_to_update(
        product_id, callback, state, session
    )
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал категорию для обновления."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе данных для обновления категории"
)
@category_router.callback_query(
    CategoryUpdateState.select,
    and_f(
        F.data != ADMIN_UPDATE_OPTIONS.get("name"),
        F.data != ADMIN_UPDATE_OPTIONS.get("content"),
    ),
)
async def select_category_data_to_update(
    callback: CallbackQuery, session: AsyncSession
):
    """Выбор поля для редактирования категории."""
    await category_update_manager.select_data_to_update(callback, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал данные для обновления категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении имени категории"
)
@category_router.callback_query(
    CategoryUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("name")
)
async def category_name_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое название категории."""
    await category_update_manager.change_obj_name(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} обновил название категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении содержания категории"
)
@category_router.callback_query(
    CategoryUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("content")
)
async def about_url_update(callback: CallbackQuery, state: FSMContext):
    """Изменить содержание категории."""
    await category_update_manager.change_obj_content(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} обновил содержание категории."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении информации о категории в БД"
)
@category_router.message(
    or_f(
        CategoryUpdateState.name,
        CategoryUpdateState.media,
        CategoryUpdateState.url,
        CategoryUpdateState.description,
    ),
    or_f(
        F.text,
        F.photo,
    ),
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Внести изменения информации о категории в БД."""
    await category_update_manager.update_obj_in_db(message, state, session)
    logger.info(
        f"Пользователь {message.from_user.id} обновил информацию о категории в БД."
    )
