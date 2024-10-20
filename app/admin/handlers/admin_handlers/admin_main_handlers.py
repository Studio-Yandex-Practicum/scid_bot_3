import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from admin.admin_settings import (
    MAIN_MENU_TEXT,
    PORTFOLIO_MENU_TEXT,
    PORTFOLIO_OTHER_PROJECTS_TEXT,
    PRODUCT_LIST_TEXT,
    MAIN_MENU_OPTIONS,
    MAIN_MENU_BUTTONS,
    COMPANY_ABOUT,
    PORTFOLIO_BUTTONS,
    PORTFOLIO_MENU_OPTIONS,
    SUPPORT_OPTIONS,
    SUPPORT_MENU_TEXT,
    SUPPROT_MENU_BUTTONS,
)
from admin.filters.filters import ChatTypeFilter
from admin.keyboards.keyboards import (
    get_inline_keyboard,
    get_delete_message_keyboard,
)
from bot.exceptions import message_exception_handler
from crud.category_product import category_product_crud
from crud.info_crud import info_crud
from crud.about_crud import company_info_crud
from crud.portfolio_projects_crud import portfolio_crud
from crud.product_crud import product_crud
from models.models import ProductCategory

logger = logging.getLogger(__name__)

admin_main_router = Router()
admin_main_router.message.filter(
    ChatTypeFilter(["private"]),
)


class QuestionAnswer(StatesGroup):
    question = State()


class ProductCategoryStates(StatesGroup):
    product_id = State()
    category = State()


@admin_main_router.callback_query(F.data == "delete")
async def delete_message(callback: CallbackQuery):
    """Удалить сообщение, после коллбека 'delete'."""
    await callback.message.delete()


def extract_and_unpack(objects, *fields):
    """Извлекает указанные поля из списка объектов и распаковывает их."""
    extracted_data = [
        [getattr(obj, field) for field in fields] for obj in objects
    ]
    return zip(*extracted_data) if extracted_data else ([], [])


@message_exception_handler(log_error_text="Ошибка при получении главного меню")
@admin_main_router.callback_query(F.data == MAIN_MENU_TEXT)
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Получить главное меню через callback_query."""
    await callback.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=await get_inline_keyboard(MAIN_MENU_BUTTONS),
    )
    await state.clear()
    logger.info(f"Пользователь {callback.from_user.id} получил главное меню.")


@message_exception_handler(log_error_text="Ошибка при выводе меню с портфолио")
@admin_main_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("portfolio"))
async def portfolio_info(callback: CallbackQuery, session: AsyncSession):
    """Вывести меню с портфолио."""
    portlio_url = await portfolio_crud.get_portfolio(session)
    await callback.message.edit_text(
        PORTFOLIO_MENU_TEXT,
        reply_markup=await get_inline_keyboard(
            PORTFOLIO_BUTTONS,
            urls=[portlio_url.url],
            previous_menu=MAIN_MENU_TEXT,
            admin_update_menu=callback.data,
        ),
    )
    logger.info(f"Пользователь {callback.from_user.id} открыл меню портфолио.")


@message_exception_handler(
    log_error_text="Ошибка при получении информации о компании"
)
@admin_main_router.callback_query(
    F.data == MAIN_MENU_OPTIONS.get("company_bio")
)
async def main_info(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить список ссылок на информацию о компании."""
    await state.clear()

    about_company = await company_info_crud.get_multi(session)
    about_company_buttons, company_about_urls = extract_and_unpack(
        about_company, "name", "url"
    )
    await callback.message.edit_text(
        COMPANY_ABOUT,
        reply_markup=await get_inline_keyboard(
            options=about_company_buttons,
            previous_menu=MAIN_MENU_TEXT,
            urls=company_about_urls,
            admin_update_menu=callback.data,
        ),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} получил информацию о компании."
    )


@message_exception_handler(
    log_error_text="Ошибка при получении меню выбора раздела техподдержки"
)
@admin_main_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("support"))
async def support_menu(callback: CallbackQuery):
    """Получить меню выбора раздела техподдержки."""
    await callback.message.edit_text(
        SUPPORT_MENU_TEXT,
        reply_markup=await get_inline_keyboard(
            options=SUPPROT_MENU_BUTTONS,
            previous_menu=MAIN_MENU_TEXT,
        ),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} открыл меню техподдержки."
    )


@message_exception_handler(
    log_error_text="Ошибка при получении списка вопросов техподдержки"
)
@admin_main_router.callback_query(
    or_f(
        F.data == SUPPORT_OPTIONS.get("general_questions"),
        F.data == SUPPORT_OPTIONS.get("problems_with_products"),
    )
)
async def info_faq(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить список вопросов раздела техподдержки."""
    await state.clear()

    question_type = callback.data
    question_list = [
        question.question
        for question in await info_crud.get_all_questions_by_type(
            question_type=question_type, session=session
        )
    ]

    await callback.message.edit_text(
        callback.data,
        reply_markup=await get_inline_keyboard(
            options=question_list,
            previous_menu=MAIN_MENU_OPTIONS.get("support"),
            admin_update_menu=callback.data,
        ),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} получил список вопросов техподдержки."
    )
    await state.set_state(QuestionAnswer.question)


@message_exception_handler(
    log_error_text="Ошибка при получении списка других проектов"
)
@admin_main_router.callback_query(
    F.data == PORTFOLIO_MENU_OPTIONS.get("other_projects")
)
async def portfolio_other_projects(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить список других проектов компании."""
    await state.clear()
    projects = await portfolio_crud.get_multi(session)
    projects_names, urls = extract_and_unpack(projects, "name", "url")
    await callback.message.edit_text(
        PORTFOLIO_OTHER_PROJECTS_TEXT,
        reply_markup=await get_inline_keyboard(
            projects_names,
            previous_menu=MAIN_MENU_OPTIONS.get("portfolio"),
            urls=urls,
            admin_update_menu=callback.data,
        ),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} получил список других проектов."
    )


@message_exception_handler(
    log_error_text="Ошибка при получении списка продуктов"
)
@admin_main_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("products"))
async def get_products_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить список продуктов."""
    products: list[ProductCategory] = await product_crud.get_multi(session)
    product_names, product_id = extract_and_unpack(products, "name", "id")

    await state.clear()

    await callback.message.edit_text(
        PRODUCT_LIST_TEXT,
        reply_markup=await get_inline_keyboard(
            product_names,
            callback=product_id,
            previous_menu=MAIN_MENU_TEXT,
            admin_update_menu=callback.data,
        ),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} получил список продуктов."
    )
    await state.set_state(ProductCategoryStates.category)


@message_exception_handler(
    log_error_text="Ошибка при получении списка дополнительных вариантов продукта"
)
@admin_main_router.callback_query(ProductCategoryStates.category, F.data)
async def product_category(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить список дополнительных вариантов продукта."""
    product: ProductCategory = await product_crud.get(callback.data, session)
    categories = await category_product_crud.get_category_by_product_id(
        product.id, session
    )
    categories_name, urls = extract_and_unpack(categories, "name", "url")
    await callback.message.edit_text(
        f"{product.description}",
        reply_markup=await get_inline_keyboard(
            categories_name,
            urls=urls,
            previous_menu=MAIN_MENU_OPTIONS.get("products"),
            admin_update_menu=callback.data,
        ),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} получил список вариантов для продукта {product.name}."
    )
    await state.set_state(ProductCategoryStates.product_id)
    await state.update_data(product_id=product.id)


@message_exception_handler(
    log_error_text="Ошибка при получении данных варианта продукта"
)
@admin_main_router.callback_query(ProductCategoryStates.product_id, F.data)
async def get_product_info(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить данные варианта продукта."""
    state_data = await state.get_data()
    product_id = state_data.get("product_id")
    category = await category_product_crud.get_active_field(
        product_id=product_id, category_name=callback.data, session=session
    )

    if category.media:
        await callback.message.answer_photo(
            photo=category.media,
            caption=category.description,
            reply_markup=await get_delete_message_keyboard(),
        )
    else:
        await callback.message.answer(
            category.description,
            reply_markup=await get_delete_message_keyboard(),
        )
    logger.info(
        f"Пользователь {callback.from_user.id} получил информацию о продукте {category.name}."
    )


@message_exception_handler(
    log_error_text="Ошибка при получении ответа на вопрос из раздела Техподдержка"
)
@admin_main_router.callback_query(QuestionAnswer.question, F.data)
async def faq_answer(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить ответ на вопрос из раздела Техподдержка."""
    question_list = [
        question.question for question in await info_crud.get_multi(session)
    ]

    if callback.data not in question_list:
        return

    question = await info_crud.get_by_string(callback.data, session)
    answer = f"{callback.data}\n\n{question.answer}"

    await callback.message.answer(
        answer,
        reply_markup=await get_delete_message_keyboard(),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} получил ответ на вопрос: {callback.data}."
    )
    await state.clear()
