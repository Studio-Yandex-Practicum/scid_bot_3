from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from .admin import SectionState
from crud.category_product import category_product_crud
from crud.product_crud import product_crud
from filters.filters import ChatTypeFilter, IsAdmin
from keyboards.keyboards import (
    get_inline_confirmation_keyboard,
    get_inline_keyboard,
)
# from settings import (
#     MAIN_MENU_OPTIONS,
# )

MAIN_MENU_OPTIONS = {
    "company_bio": "Информация о компании",
    "products": "Продукты и услуги",
    "support": "Техническая поддержка",
    "portfolio": "Портфолио",
    "request_callback": "Связаться с менеджером",
}

product_router = Router()
product_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("products")


class AddProduct(StatesGroup):
    title = State()
    response = State()


class UpdateProduct(StatesGroup):
    select = State()
    title = State()
    response = State()
    confirm = State()


class DeleteProduct(AddProduct):
    confirm = State()


class AddProductInfo(StatesGroup):
    name = State()
    product_id = State()
    url = State()
    media = State()
    description = State()
    media_description = State()


async def get_products_list(session: AsyncSession):
    """Получить список названий проектов для портфолио."""

    return [project.title for project in await product_crud.get_multi(session)]


@product_router.callback_query(SectionState.product, F.data == "Добавить")
async def add_product(callback: CallbackQuery, state: FSMContext):
    """Добавить название."""

    await callback.message.answer("Введите название проекта или услуги")
    await state.set_state(AddProduct.title)


@product_router.message(AddProduct.title, F.text)
async def add_product_description(message: Message, state: FSMContext):
    """Добавить описание."""

    await state.update_data(title=message.text)
    await message.answer("Добавьте описание к продукту или услуге")
    await state.set_state(AddProduct.response)


@product_router.message(AddProduct.response, F.text)
async def creeate_product(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Создать продкет в БД."""

    await state.update_data(response=message.text)
    data = await state.get_data()

    await product_crud.create(data, session)
    await message.answer(
        "Продукт создан! Хотите добавить к нему дополнительну информацию?",
        reply_markup=await get_inline_confirmation_keyboard(
            option="Да", cancel_option=PREVIOUS_MENU
        ),
    )

    await state.set_state(AddProductInfo.product_id)


@product_router.callback_query(AddProductInfo.product_id, F.data == "Да")
async def add_product_categoty(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Добавить основные варианты для продукта."""

    await state.clear()

    last_product = await product_crud.get_last_added_product(session)
    await state.update_data(product_id=last_product.id)

    await callback.message.answer(
        "Введите название для дополнительной информации"
    )

    await state.set_state(AddProductInfo.name)


@product_router.message(AddProductInfo.name, F.text)
async def add_product_category_name(message: Message, state: FSMContext):
    """Выбрать тип данных для основных вариантов."""

    await state.update_data(name=message.text)

    await message.answer(
        "Выберете способ передачи информации:",
        reply_markup=await get_inline_keyboard(
            ["Ссылка", "Текст", "Картинка"], previous_menu=PREVIOUS_MENU
        ),
    )


@product_router.callback_query(
    or_f(AddProductInfo.name, AddProductInfo.description),
    or_f(F.data == "Ссылка", F.data == "Текст", F.data == "Картинка"),
)
async def add_product_category_data(
    callback: CallbackQuery, state: FSMContext
):
    """Добавить информацию в основной вариант."""

    if callback.data == "Ссылка":
        await state.set_state(AddProductInfo.url)
        info_type = "ссылку"
    elif callback.data == "Текст":
        await state.set_state(AddProductInfo.description)
        info_type = "текст"
    elif callback.data == "Картинка":
        await state.set_state(AddProductInfo.media)
        info_type = "Картинку"
    await callback.message.answer(f"Добавьте {info_type}")


@product_router.message(AddProductInfo.media, F.photo)
async def add_media_description(message: Message, state: FSMContext):
    """Добавить описание к картинке."""

    await state.update_data(media=message.photo[-1].file_id)

    await message.answer(
        "Добавить описание к картинке?",
        reply_markup=await get_inline_confirmation_keyboard(
            "Текст", cancel_option="Нет"
        ),
    )

    print(await state.get_data())
    await state.set_state(AddProductInfo.description)


@product_router.message(
    or_f(AddProductInfo.description, AddProductInfo.url),
    or_f(F.text, F.photo, F.data == "Нет"),
)
async def create_product_with_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Создать вариант для продукта в БД и предложить добавить следующий."""

    current_state = await state.get_state()
    if current_state == AddProductInfo.description:
        await state.update_data(description=message.text)
    elif current_state == AddProductInfo.url:
        await state.update_data(url=message.text)
    data = await state.get_data()

    await category_product_crud.create(data, session)
    await message.answer(
        "Информация добавлена! Добавить еще?",
        reply_markup=await get_inline_confirmation_keyboard(
            option="Да", cancel_option=PREVIOUS_MENU
        ),
    )

    await state.set_state(AddProductInfo.product_id)


@product_router.callback_query(SectionState.product, F.data == "Удалить")
async def product_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта на удаление."""

    await callback.message.edit_text(
        "Какой проект вы хотите удалить?",
        reply_markup=await get_inline_keyboard(
            options=await get_products_list(session),
            previous_menu=PREVIOUS_MENU,
        ),
    )

    await state.set_state(DeleteProduct.title)


@product_router.callback_query(DeleteProduct.title, F.data)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтверждение удаления."""

    portfolio_project = await product_crud.get_by_product_name(
        callback.data, session
    )
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить "
        f"этот проект?\n\n {portfolio_project.title}",
        reply_markup=await get_inline_confirmation_keyboard(
            option=portfolio_project.title, cancel_option=PREVIOUS_MENU
        ),
    )

    await state.set_state(DeleteProduct.confirm)


@product_router.callback_query(DeleteProduct.confirm, F.data != PREVIOUS_MENU)
async def delete_product(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить продукт из БД."""

    portfolio_project = await product_crud.get_by_product_name(
        callback.data, session
    )

    await product_crud.remove(portfolio_project, session)
    await callback.message.edit_text(
        "Услуга удалена!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )

    await state.clear()


@product_router.callback_query(SectionState.product, F.data == "Изменить")
async def product_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Выбор продукта для редактирования."""

    await callback.message.edit_text(
        "Какую услугу вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            options=await get_products_list(session),
            previous_menu=PREVIOUS_MENU,
        ),
    ),

    await state.set_state(UpdateProduct.select)


@product_router.callback_query(
    UpdateProduct.select,
    and_f(
        F.data != "Название проекта",
        F.data != "Описание",
        F.data != PREVIOUS_MENU,
    ),
)
async def update_portfolio_project_choise(
    callback: CallbackQuery, state: FSMContext
):
    """Выбор поля для редактирования."""

    await state.update_data(select=callback.data)
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            ["Название проекта", "Описание"], previous_menu=PREVIOUS_MENU
        ),
    )


@product_router.callback_query(
    UpdateProduct.select, F.data == "Название проекта"
)
async def about_name_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Ввести новое название продукта."""

    product_data = await state.get_data()
    product_name = product_data.get("select")

    await callback.message.answer(
        f"Текущее название:\n\n {product_name}\n\n Введите новое название"
    )

    await state.set_state(UpdateProduct.title)


@product_router.callback_query(UpdateProduct.select, F.data == "Описание")
async def about_url_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Ввести новое описание продукта."""

    product_data = await state.get_data()
    product_title = product_data.get("select")
    product = await product_crud.get_by_product_name(product_title, session)

    await callback.message.answer(
        f"Текущее описание:\n\n {product.response}\n\n Введите новое описание"
    )

    await state.set_state(UpdateProduct.response)


@product_router.message(
    or_f(UpdateProduct.title, UpdateProduct.response), F.text
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Внести изменения продукта в БД."""

    current_state = await state.get_state()
    old_data = await state.get_data()
    old_product_data = await product_crud.get_by_product_name(
        old_data.get("select"), session
    )

    if current_state == UpdateProduct.title:
        await state.update_data(title=message.text)
    elif current_state == UpdateProduct.response:
        await state.update_data(response=message.text)

    update_data = await state.get_data()
    await product_crud.update(old_product_data, update_data, session)

    await message.answer(
        "Информация обновлена!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )

    await state.clear()
