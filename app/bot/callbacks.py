import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from admin.keyboards.keyboards import get_delete_message_keyboard
from helpers import get_user_id, start_inactivity_timer
from core.bot_setup import bot
from bot.exceptions import message_exception_handler
from bot.keyborads import (
    get_back_to_main_keyboard,
    get_company_portfolio_choice,
    list_of_projects_keyboard,
    main_keyboard,
    faq_or_problems_with_products_inline_keyboard,
    category_type_inline_keyboard,
    inline_products_and_services,
    get_company_information_keyboard,
    support_keyboard
)
from crud import (
    info_crud,
    category_product_crud,
    portfolio_crud,
    products_crud,
)
import bot.bot_const as bc
from loggers.log import setup_logging


router = Router()

setup_logging()
logger = logging.getLogger(__name__)


@message_exception_handler(log_error_text="Ошибка при выводе списка проектов.")
@router.callback_query(F.data == "show_projects")
async def show_projects(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Выводит список проектов компании."""

    await callback.answer()

    user_id = get_user_id(callback)

    await callback.message.edit_text(
        bc.MESSAGE_FOR_SHOW_PROJECTS,
        reply_markup=await list_of_projects_keyboard(session),
    )

    logger.info(f"Пользователь {user_id} запросил список проектов")

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text="Ошибка при возврате в основное меню."
)
@router.callback_query(F.data == "back_to_main_menu")
async def previous_choice(callback: CallbackQuery, state: FSMContext) -> None:
    """Возвращает в основное меню."""

    await callback.answer()

    await state.clear()

    user_id = get_user_id(callback)

    await callback.message.edit_text(
        bc.MESSAGE_FOR_PREVIOUS_CHOICE, reply_markup=main_keyboard
    )

    logger.info(f"Пользователь {user_id} вернулся в основное меню")


@message_exception_handler(log_error_text="Ошибка при получении вопросов.")
@router.callback_query(F.data.in_(("get_faq", "get_problems_with_products")))
async def get_questions(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Инлайн вывод общих вопросов и проблем с продуктами."""

    await callback.answer()

    user_id = get_user_id(callback)

    question_type = (
        "GENERAL_QUESTIONS"
        if callback.data == "get_faq"
        else "PROBLEMS_WITH_PRODUCTS"
    )

    await callback.message.edit_text(
        bc.MESSAGE_FOR_GET_QUESTIONS,
        reply_markup=await faq_or_problems_with_products_inline_keyboard(
            question_type, session
        ),
    )

    logger.info(
        f"Пользователь {user_id} " f"запросил {question_type.lower()}."
    )

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text="Ошибка при получении ответа на вопрос."
)
@router.callback_query(F.data.startswith("answer:"))
async def get_faq_answer(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Вывод ответа на выбранный вопрос."""

    await callback.answer()

    user_id = get_user_id(callback)

    question = await info_crud.get(callback.data.split(":")[1], session)

    if question:
        await callback.message.answer(
            text=f"{question.question}\n\n {question.answer}",
            reply_markup=await get_delete_message_keyboard(),
        )
    else:
        await callback.message.edit_text(bc.QUESTION_NOT_FOUND)

    logger.info(
        f"Пользователь {user_id} запросил "
        f"ответ на вопрос {callback.data.split(':')[1]} "
    )

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text="Ошибка при возврате к выбору продуктов."
)
@router.callback_query(F.data == "back_to_previous_menu")
async def back_to_products(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Возвращает к выбору продуктов."""

    await callback.answer()

    user_id = get_user_id(callback)

    await callback.message.edit_text(
        text=bc.MESSAGE_FOR_BACK_TO_PRODUCTS,
        reply_markup=await inline_products_and_services(session),
    )

    logger.info(f"Пользователь {user_id} вернулся к выбору продуктов.")

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text="Ошибка при запросе ответа для выбранной категории."
)
@router.callback_query(F.data.startswith("category_"))
async def get_response_by_title(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Возвращает заготовленный ответ на выбранную категорию."""

    await callback.answer()

    user_id = get_user_id(callback)

    product_id = int(callback.data.split("_")[1])
    product = await products_crud.get(product_id, session)

    await callback.message.edit_text(
        text=product.description,
        reply_markup=await category_type_inline_keyboard(product.id, session),
    )

    logger.info(f"Пользователь {user_id} выбрал категорию {product_id}.")

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(log_error_text="Ошибка при показе портфолио.")
@router.callback_query(F.data == "view_portfolio")
async def view_portfolio(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Показ портфолио компании."""

    await callback.answer()

    user_id = get_user_id(callback)

    url = await portfolio_crud.get_portfolio(session)
    await callback.message.edit_text(
        bc.MESSAGE_FOR_VIEW_PORTFOLIO,
        reply_markup=await get_company_portfolio_choice(url=url.url),
    )

    logger.info(f"Пользователь {user_id} запросил портфолио.")

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text="Ошибка при запросе информации о компании."
)
@router.callback_query(F.data == "company_info")
async def company_info(callback: CallbackQuery, session: AsyncSession) -> None:
    """Информация о компании."""

    await callback.answer()

    user_id = get_user_id(callback)

    await callback.message.edit_text(
        bc.MESSAGE_FOR_COMPANY_INFO,
        reply_markup=await get_company_information_keyboard(session),
    )

    logger.info(f"Пользователь {user_id} " f"запросил информацию о компании. ")

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(log_error_text="Ошибка при запросе техподдержки.")
@router.callback_query(F.data == "tech_support")
async def get_support(callback: CallbackQuery) -> None:
    """Выводит виды тех. поддержки."""

    await callback.answer()

    user_id = get_user_id(callback)

    await callback.message.edit_text(
        bc.MESSAGE_FOR_GET_SUPPORT, reply_markup=support_keyboard
    )

    logger.info(f"Пользователь {user_id} запросил техподдержку.")

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text="Ошибка при запросе информации о продуктах и услугах."
)
@router.callback_query(F.data == "products_services")
async def products_services(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Информация о продуктах и услугах."""

    await callback.answer()

    user_id = get_user_id(callback)

    await callback.message.edit_text(
        bc.MESSAGE_FOR_PRODUCTS_SERVICES,
        reply_markup=await inline_products_and_services(session),
    )

    logger.info(
        f"Пользователь {user_id} запросил "
        f"информацию о продуктах и услугах. "
    )

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(
    log_error_text='Ошибка при ответе "нет" для составления фидбека.'
)
@router.callback_query(F.data == "get_feedback_no")
async def get_feedback_no(callback: CallbackQuery) -> None:
    """Ответ на выбор 'Нет'."""

    await callback.answer()

    await callback.message.answer(
        bc.MESSAGE_FOR_GET_FEEDBACK_NO,
        reply_markup=await get_back_to_main_keyboard(),
    )


@message_exception_handler(
    log_error_text="Ошибка при ответе на выбранный тип категории."
)
@router.callback_query(F.data.startswith("show_category"))
async def process_category_callback(callback: CallbackQuery, session):

    await callback.answer()

    user_id = get_user_id(callback)

    category_id = callback.data.split(":")[1]

    category = await category_product_crud.get(category_id, session)
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

    await start_inactivity_timer(callback.message, user_id, bot)


@message_exception_handler(log_error_text="Ошибка при возврате назад.")
@router.callback_query(F.data.startswith("back"))
async def process_back_callback(callback: CallbackQuery):

    await callback.answer()

    user_id = get_user_id(callback)

    photo_message_id = callback.data.split(":")[1]

    await callback.message.bot.delete_message(
        callback.message.chat.id, photo_message_id
    )

    await callback.message.delete()

    await start_inactivity_timer(callback.message, user_id, bot)
