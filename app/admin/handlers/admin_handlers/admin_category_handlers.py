from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.handlers.admin_handlers.admin import SectionState
from admin.filters.filters import ChatTypeFilter, IsAdmin
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
from crud.category_product import category_product_crud
from crud.product_crud import product_crud

category_router = Router()
category_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

PREVIOUS_MENU = "Назад"

category_create_manager = CreateCategoryManager(PREVIOUS_MENU)
category_update_manager = UpdateCategoryManager(PREVIOUS_MENU)
category_delete_manager = DeleteCategoryManager(PREVIOUS_MENU)


async def get_categoties_by_product_id(state: FSMContext):
    """Получить id продукта из состояния."""
    fsm_data = await state.get_data()
    return fsm_data.get("product_id")


@category_router.callback_query(
    or_f(
        CategoryCreateState(),
        CategoryUpdateState(),
        CategoryDeleteState(),
        SectionState.category,
    ),
    or_f(F.data == PREVIOUS_MENU),
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


@category_router.callback_query(
    SectionState.category, F.data == ADMIN_BASE_OPTIONS.get("create")
)
async def select_new_category_type(callback: CallbackQuery, state: FSMContext):
    """Выбрать тип данных для дополнительной информации о продукте."""
    await category_create_manager.select_data_type(callback, state)


@category_router.callback_query(
    CategoryCreateState.select,
    or_f(
        F.data == ADMIN_CONTENT_OPTIONS.get("url"),
        F.data == ADMIN_CONTENT_OPTIONS.get("description"),
        F.data == ADMIN_CONTENT_OPTIONS.get("media"),
    ),
)
async def add_product_category_name(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Добавить название."""
    product_id = await get_categoties_by_product_id(state)
    await category_create_manager.add_obj_name(product_id, callback, state)


@category_router.message(CategoryCreateState.url, F.text)
async def add_product_category_url(message: Message, state: FSMContext):
    """Добавить ссылку."""
    await category_create_manager.add_obj_url(message, state)


@category_router.message(CategoryCreateState.description, F.text)
async def add_product_category_description(
    message: Message, state: FSMContext
):
    """Добавить текст."""
    await category_create_manager.add_obj_description(message, state)


@category_router.message(CategoryCreateState.media, F.text)
async def add_product_category_media(message: Message, state: FSMContext):
    """Добавить картинку."""
    await category_create_manager.add_obj_media(message, state)


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
    """
    Создать информацию для продукта в БД и предложить добавить следующий.
    """
    await category_create_manager.add_obj_to_db(message, state, session)


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


@category_router.callback_query(CategoryDeleteState.select, F.data)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтверждение удаления."""
    await category_delete_manager.confirm_delete(callback, state, session)


@category_router.callback_query(
    CategoryDeleteState.confirm, F.data != PREVIOUS_MENU
)
async def delete_category(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить информацию из БД."""
    await category_delete_manager.delete_obj(callback, state, session)


@category_router.callback_query(
    SectionState.category, F.data == ADMIN_BASE_OPTIONS.get("update")
)
async def category_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор информации для редактирования."""
    product_id = await get_categoties_by_product_id(state)
    await category_update_manager.select_obj_to_update(
        product_id, callback, state, session
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
    """Выбор поля для редактирования."""
    await category_update_manager.select_data_to_update(callback, session)


@category_router.callback_query(
    CategoryUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("name")
)
async def category_name_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое название информации."""
    await category_update_manager.change_obj_name(callback, state)


@category_router.callback_query(
    CategoryUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("content")
)
async def about_url_update(callback: CallbackQuery, state: FSMContext):
    """Изменить содержание информации."""
    await category_update_manager.change_obj_content(callback, state)


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
    """Внести изменения информации в БД."""
    await category_update_manager.update_obj_in_db(message, state, session)
