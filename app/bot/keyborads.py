from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from crud import (
    company_info_crud,
    category_product_crud,
    info_crud,
    portfolio_crud,
    products_crud,
)

back_to_main_menu = InlineKeyboardButton(
    text="Вернуться в главное меню", callback_data="back_to_main_menu"
)

back_to_previous_menu = InlineKeyboardButton(
    text="Назад к продуктам", callback_data="back_to_previous_menu"
)

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Посмотреть портфолио", callback_data="view_portfolio"
            )
        ],
        [
            InlineKeyboardButton(
                text="Информация о компании", callback_data="company_info"
            )
        ],
        [
            InlineKeyboardButton(
                text="Продукты и услуги", callback_data="products_services"
            )
        ],
        [
            InlineKeyboardButton(
                text="Техническая поддержка", callback_data="tech_support"
            )
        ],
        [
            InlineKeyboardButton(
                text="Связаться с менеджером", callback_data="contact_manager"
            )
        ],
    ]
)

async def get_back_to_main_keyboard():
    """Клавиатура для возвращения на главное меню."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(back_to_main_menu)
    return keyboard.adjust(1).as_markup()

async def get_company_information_keyboard(session: AsyncSession):

    builder = InlineKeyboardBuilder()

    presentation = await company_info_crud.get_by_string(
        "Презентация компании", session
    )
    card = await company_info_crud.get_by_string("Карточка компании", session)

    if presentation:
        builder.add(
            InlineKeyboardButton(text=presentation.name, url=presentation.url)
        )
    if card:
        builder.add(InlineKeyboardButton(text=card.name, url=card.url))

    builder.add(back_to_main_menu)

    return builder.adjust(1).as_markup()


async def inline_products_and_services(session: AsyncSession):
    """Инлайн клавиатура для продуктов и услуг."""

    keyboard = InlineKeyboardBuilder()

    objects_in_db = await products_crud.get_multi(session)

    for obj in objects_in_db:
        keyboard.add(
            InlineKeyboardButton(
                text=obj.name, callback_data=f"category_{obj.id}"
            )
        )

    keyboard.add(back_to_main_menu)

    return keyboard.adjust(1).as_markup()


async def get_company_portfolio_choice(url: str):
    """Инлайн клавиатура для портфолио."""
    company_portfolio_choice = InlineKeyboardBuilder()
    company_portfolio_choice.add(
        InlineKeyboardButton(text="Портфолио", url=url)
    )
    company_portfolio_choice.add(
        InlineKeyboardButton(
            text="Перейти к проектам", callback_data="show_projects"
        )
    )
    company_portfolio_choice.add(back_to_main_menu)
    return company_portfolio_choice.adjust(1).as_markup(resize_keyboard=True)


async def list_of_projects_keyboard(session: AsyncSession):
    """Инлайн вывод проектов с данными из БД."""

    projects = await portfolio_crud.get_multi(session)

    keyboard = InlineKeyboardBuilder()

    for project in projects:
        keyboard.add(InlineKeyboardButton(text=project.name, url=project.url))

    keyboard.add(back_to_main_menu)

    return keyboard.adjust(1).as_markup()


support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="F.A.Q", callback_data="get_faq")],
        [
            InlineKeyboardButton(
                text="Проблемы с продуктами",
                callback_data="get_problems_with_products",
            )
        ],
        [
            InlineKeyboardButton(
                text="Запрос на обратный звонок",
                callback_data="callback_request",
            )
        ],
        [back_to_main_menu],
    ]
)


async def faq_or_problems_with_products_inline_keyboard(
    question_type: str, session: AsyncSession
) -> InlineKeyboardMarkup:
    """Инлайн-клавиатуры для f.a.q вопросов или проблем с продуктами."""

    questions = await info_crud.get_all_questions_by_type(
        question_type, session
    )

    keyboard = InlineKeyboardBuilder()
    for question in questions:
        keyboard.add(
            InlineKeyboardButton(
                text=question.question, callback_data=f"answer:{question.id}"
            )
        )

    keyboard.add(back_to_main_menu)

    return keyboard.adjust(1).as_markup()


async def category_type_inline_keyboard(
    product_id: str, session: AsyncSession
) -> InlineKeyboardMarkup:
    """Инлайн клавиатура для типов в категориях."""

    category_types = await category_product_crud.get_category_by_product_id(
        product_id, session
    )

    keyboard = InlineKeyboardBuilder()

    for category_type in category_types:
        keyboard.add(
            InlineKeyboardButton(
                text=category_type.name,
                url=category_type.url,
                callback_data=f"show_category:{category_type.id}",
            )
        )

    keyboard.add(back_to_previous_menu)

    return keyboard.adjust(1).as_markup()


get_feedback_keyboard = (
    InlineKeyboardBuilder()
    .add(
        InlineKeyboardButton(text="Да", callback_data="get_feedback_yes"),
        InlineKeyboardButton(text="Нет", callback_data="get_feedback_no"),
    )
    .adjust(1)
    .as_markup()
)
