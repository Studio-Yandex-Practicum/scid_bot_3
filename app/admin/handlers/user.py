from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from admin.admin_settings import (
    PORTFOLIO_DEFAULT_DATA,
    PORTFOLIO_MENU_TEXT,
    PORTFOLIO_OTHER_PROJECTS_TEXT,
    PRODUCT_LIST_TEXT,
    BASE_BUTTONS,
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
from crud.category_product import category_product_crud
from crud.info_crud import info_crud
from crud.about_crud import company_info_crud
from crud.portfolio_projects_crud import portfolio_crud
from crud.product_crud import product_crud


user_router = Router()
user_router.message.filter(
    ChatTypeFilter(["private"]),
)


class QuestionAnswer(StatesGroup):
    question = State()


class ProductCategory(StatesGroup):
    product_id = State()
    category = State()


@user_router.callback_query(F.data == "delete")
async def delete_message(callback: CallbackQuery):
    await callback.message.delete()


@user_router.callback_query(F.data == BASE_BUTTONS.get("main_menu"))
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Получить основное меню бота через callback_query."""

    await callback.message.edit_text(
        BASE_BUTTONS.get("main_menu"),
        reply_markup=await get_inline_keyboard(MAIN_MENU_BUTTONS),
    )
    await state.clear()


@user_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("portfolio"))
async def portfolio_info(callback: CallbackQuery, session: AsyncSession):
    portlio_url = await portfolio_crud.get_portfolio(session)
    await callback.message.edit_text(
        PORTFOLIO_MENU_TEXT,
        reply_markup=await get_inline_keyboard(
            PORTFOLIO_BUTTONS,
            urls=[
                portlio_url.url,
            ],
            previous_menu=BASE_BUTTONS.get("main_menu"),
            admin_update_menu=callback.data,
        ),
    )


@user_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("company_bio"))
async def main_info(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить список ссылок на информацию о компании."""

    await state.clear()

    about_company_data = await company_info_crud.get_multi(session)
    about_company_buttons = [
        data.name
        for data in about_company_data
        if data.name != PORTFOLIO_DEFAULT_DATA.get("name")
    ]

    company_about_urls = [data.url for data in about_company_data]

    await callback.message.edit_text(
        COMPANY_ABOUT,
        reply_markup=await get_inline_keyboard(
            options=about_company_buttons,
            previous_menu=BASE_BUTTONS.get("main_menu"),
            urls=company_about_urls,
            admin_update_menu=callback.data,
        ),
    )


@user_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("support"))
async def support_menu(callback: CallbackQuery):
    """Получить меню выбора раздела техподдержки."""

    await callback.message.edit_text(
        SUPPORT_MENU_TEXT,
        reply_markup=await get_inline_keyboard(
            options=SUPPROT_MENU_BUTTONS,
            previous_menu=BASE_BUTTONS.get("main_menu"),
        ),
    )


@user_router.callback_query(
    or_f(
        F.data == SUPPORT_OPTIONS.get("general_questions"),
        F.data == SUPPORT_OPTIONS.get("problems_with_products"),
    )
)
async def info_faq(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
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

    await state.set_state(QuestionAnswer.question)


@user_router.callback_query(
    F.data == PORTFOLIO_MENU_OPTIONS.get("other_projects")
)
async def portfolio_other_projects(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить список других проектов компании."""

    await state.clear()
    projects = await portfolio_crud.get_multi(session)
    projects_names = [project.name for project in projects]
    urls = [project.url for project in projects]

    await callback.message.edit_text(
        PORTFOLIO_OTHER_PROJECTS_TEXT,
        reply_markup=await get_inline_keyboard(
            projects_names,
            previous_menu=MAIN_MENU_OPTIONS.get("portfolio"),
            urls=urls,
            admin_update_menu=callback.data,
        ),
    )


@user_router.callback_query(F.data == MAIN_MENU_OPTIONS.get("products"))
async def get_products_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить список продуктов."""

    products = [
        product.name for product in await product_crud.get_multi(session)
    ]

    await state.clear()

    await callback.message.edit_text(
        PRODUCT_LIST_TEXT,
        reply_markup=await get_inline_keyboard(
            products,
            previous_menu=BASE_BUTTONS.get("main_menu"),
            admin_update_menu=callback.data,
        ),
    )

    await state.set_state(ProductCategory.category)


@user_router.callback_query(ProductCategory.category, F.data)
async def product_category(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    """Получить список дополнительных вариантов продукта."""

    product = await product_crud.get_by_product_name(callback.data, session)
    categories = await category_product_crud.get_category_by_product_id(
        product.id, session
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
    await state.update_data(product_id=product.id)


@user_router.callback_query(ProductCategory.product_id, F.data)
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


@user_router.callback_query(QuestionAnswer.question, F.data)
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
