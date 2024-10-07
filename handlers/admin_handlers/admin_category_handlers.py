from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.admin_handlers.admin import SectionState
from CRUD.category_product import category_product_crud
from CRUD.product_crud import product_crud
from filters.filters import ChatTypeFilter, IsAdmin
from handlers.user import ProductCategory
from keyboards.keyboards import (
    get_inline_confirmation_keyboard,
    get_inline_keyboard,
)
from settings import MAIN_MENU_OPTIONS, admin_list

category_router = Router()
category_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class AddCategory(StatesGroup):
    name = State()
    url = State()
    media = State()
    description = State()


class UpdateCategory(StatesGroup):
    name = State()
    url = State()
    media = State()
    description = State()
    select = State()


class DeleteCategory(AddCategory):
    confirm = State()


async def get_category_list(state: FSMContext, session: AsyncSession):
    """Получить список вариантов для проекта."""
    fsm_data = await state.get_data()
    product_id = fsm_data.get("product_id")
    return [
        category
        for category in await category_product_crud.get_multi_for_product(
            product_id, session
        )
    ]


async def get_category_by_name(
    field_name: str, state: FSMContext, session: AsyncSession
):
    fsm_data = await state.get_data()
    product_id = fsm_data.get("product_id")
    return await category_product_crud.get_category_by_name(
        product_id=product_id, field_name=field_name, session=session
    )


@category_router.callback_query(
    or_f(
        AddCategory(),
        UpdateCategory(),
        DeleteCategory(),
        SectionState.category,
    ),
    or_f(F.data == "Назад", F.data == "Отмена"),
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
        f"{product.response}",
        reply_markup=await get_inline_keyboard(
            categories_by_name,
            urls=urls,
            previous_menu=MAIN_MENU_OPTIONS.get("products"),
            is_admin=callback.from_user.id in admin_list,
            admin_update_menu=callback.data,
        ),
    )
    await state.set_state(ProductCategory.product_id)


@category_router.callback_query(SectionState.category, F.data == "Добавить")
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    """Добавить основные варианты для продукта."""
    await callback.message.answer(
        "Введите название для дополнительной информации",
        reply_markup=await get_inline_keyboard(previous_menu="Назад"),
    )
    await state.set_state(AddCategory.name)


@category_router.message(AddCategory.name, F.text)
async def add_product_category_name(
    message: Message,
    state: FSMContext,
):
    """Выбрать тип данных для основных вариантов."""

    await state.update_data(name=message.text)
    await message.answer(
        "Выберете способ передачи информации:",
        reply_markup=await get_inline_keyboard(
            ["Ссылка", "Текст", "Картинка"],
            previous_menu="Назад",
        ),
    )


@category_router.callback_query(
    or_f(AddCategory.name, AddCategory.description),
    or_f(F.data == "Ссылка", F.data == "Текст", F.data == "Картинка"),
)
async def add_product_category_data(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Добавить информацию в основной вариант."""

    if callback.data == "Ссылка":
        info_type = "ссылку"
        await state.set_state(AddCategory.url)
    elif callback.data == "Текст":
        info_type = "текст"
        fsm_data = await state.get_data()
        category_name = fsm_data.get("select")
        product_id = fsm_data.get("product_id")
        category = await category_product_crud.get_category_by_name(
            product_id, category_name, session
        )
        if category:
            await state.set_state(UpdateCategory.description)
        else:
            await state.set_state(AddCategory.description)
    elif callback.data == "Картинка":
        info_type = "Картинку"
        await state.set_state(AddCategory.media)
    await callback.message.answer(
        f"Добавьте {info_type}",
        reply_markup=await get_inline_keyboard(previous_menu="Назад"),
    )


@category_router.message(
    or_f(AddCategory.media, UpdateCategory.media), F.photo
)
async def add_media_description(message: Message, state: FSMContext):
    """Добавить описание к картинке."""
    await state.update_data(media=message.photo[-1].file_id)
    await message.answer(
        "Добавить описание к картинке?",
        reply_markup=await get_inline_confirmation_keyboard(
            "Текст", cancel_option="Нет"
        ),
    )
    await state.set_state(AddCategory.description)


@category_router.message(
    or_f(AddCategory.description, AddCategory.url),
    or_f(F.text, F.photo, F.data == "Нет"),
)
async def create_product_with_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Создать вариант для продукта в БД и предложить добавить следующий."""
    current_state = await state.get_state()
    if current_state == AddCategory.description:
        await state.update_data(description=message.text)
    elif current_state == AddCategory.url:
        await state.update_data(url=message.text)
    data = await state.get_data()
    await category_product_crud.create(data, session)
    await message.answer(
        "Информация добавлена!",
        reply_markup=await get_inline_keyboard(previous_menu="Назад"),
    )


@category_router.callback_query(SectionState.category, F.data == "Удалить")
async def product_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта на удаление."""
    categories = [
        category.name for category in await get_category_list(state, session)
    ]
    await callback.message.edit_text(
        "Какой проект вы хотите удалить?",
        reply_markup=await get_inline_keyboard(
            options=categories,
            previous_menu="Назад",
        ),
    )
    await state.set_state(DeleteCategory.name)


@category_router.callback_query(DeleteCategory.name, F.data)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтверждение удаления."""
    category = await get_category_by_name(callback.data, state, session)
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить этот проект?\n\n {category.name}",
        reply_markup=await get_inline_confirmation_keyboard(
            option=category.name, cancel_option="Назад"
        ),
    )
    await state.set_state(DeleteCategory.confirm)


@category_router.callback_query(DeleteCategory.confirm, F.data != "Назад")
async def delete_product(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить продукт из БД."""
    category = await get_category_by_name(callback.data, state, session)
    await category_product_crud.remove(category, session)
    await callback.message.edit_text(
        "Услуга удалена!",
        reply_markup=await get_inline_keyboard(previous_menu="Назад"),
    )


@category_router.callback_query(SectionState.category, F.data == "Изменить")
async def product_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта для редактирования."""
    categories = [
        category.name for category in await get_category_list(state, session)
    ]
    await callback.message.edit_text(
        "Какую услугу вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            options=categories, previous_menu="Назад"
        ),
    )
    await state.set_state(UpdateCategory.select)


@category_router.callback_query(
    UpdateCategory.select,
    and_f(F.data != "Название", F.data != "Содержание"),
)
async def update_portfolio_project_choise(
    callback: CallbackQuery, state: FSMContext
):
    """Выбор поля для редактирования."""
    await state.update_data(select=callback.data)
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            ["Название", "Содержание"], previous_menu="Назад"
        ),
    )


@category_router.callback_query(UpdateCategory.select, F.data == "Название")
async def about_name_update(callback: CallbackQuery, state: FSMContext):
    """Ввести новое название продукта."""
    fsm_data = await state.get_data()
    category_name = fsm_data.get("select")
    await callback.message.answer(
        f"Текущее название:\n\n {category_name}\n\n Введите новое название"
    )
    await state.set_state(UpdateCategory.name)


@category_router.callback_query(UpdateCategory.select, F.data == "Содержание")
async def about_url_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Изменить содержание продукта."""
    fsm_data = await state.get_data()
    category_choice = fsm_data.get("select")
    category = await get_category_by_name(category_choice, state, session)
    if category.url:
        await callback.message.answer(
            f"Текущий адрес ссылки:\n\n {category.url}\n\n Введите новый адрес ссылки:"
        )
        await state.set_state(UpdateCategory.url)
    if category.description and not category.media:
        await callback.message.answer(
            f"Текущий текст:\n\n {category.description}\n\n Введите новый текст:"
        )
        await state.set_state(UpdateCategory.description)
    if category.media:
        await callback.message.answer("Текущая картинка:")
        await callback.message.answer_photo(
            photo=category.media, caption=category.description
        )
        await callback.message.answer(
            "Добавьте новую картинку и описание",
            reply_markup=await get_inline_keyboard(previous_menu="Назад"),
        )
        await state.set_state(UpdateCategory.media)


@category_router.message(
    or_f(
        UpdateCategory.name,
        UpdateCategory.media,
        UpdateCategory.url,
        UpdateCategory.description,
    ),
    or_f(
        F.text,
        F.photo,
    ),
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Внести изменения продукта в БД."""
    current_state = await state.get_state()
    old_data = await state.get_data()
    print(old_data)
    old_category_data = await get_category_by_name(
        old_data.get("select"), state, session
    )
    if current_state == UpdateCategory.name:
        await state.update_data(name=message.text)
    elif current_state == UpdateCategory.url:
        await state.update_data(url=message.text)
    elif current_state == UpdateCategory.media:
        await state.update_data(media=message.photo)
    elif current_state == UpdateCategory.description:
        await state.update_data(description=message.text)
    update_data = await state.get_data()
    await category_product_crud.update(old_category_data, update_data, session)
    await message.answer(
        "Информация обновлена!",
        reply_markup=await get_inline_keyboard(previous_menu="Назад"),
    )
