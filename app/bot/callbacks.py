import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.exceptions import message_exception_handler
from bot.keyborads import (
    list_of_projects_keyboard, main_keyboard,
    faq_or_problems_with_products_inline_keyboard,
    category_type_inline_keyboard, inline_products_and_services,
    company_information_keyboard, company_portfolio_choice,
    support_keyboard, back_to_main_menu
)
from crud.questions import get_question_by_id
from crud.projects import get_title_by_id, response_text_by_id
import bot.bot_const as bc


router = Router()

logger = logging.getLogger(__name__)


@message_exception_handler(
    log_error_text='Ошибка при выводе списка проектов для'
)
@router.callback_query(F.data == 'show_projects')
async def show_projects(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Выводит список проектов компании."""

    await callback.answer()

    await callback.message.edit_text(
        bc.MESSAGE_FOR_SHOW_PROJECTS,
        reply_markup=await list_of_projects_keyboard(session)
    )

    logger.info(
        f'Пользователь {callback.from_user.id} запросил список проектов'
    )


@message_exception_handler(
    log_error_text='Ошибка при возврате в основное меню для'
)
@router.callback_query(F.data == 'back_to_main_menu')
async def previous_choice(callback: CallbackQuery) -> None:
    """Возвращает в основное меню."""

    await callback.answer()

    await callback.message.edit_text(
        bc.MESSAGE_FOR_PREVIOUS_CHOICE,
        reply_markup=main_keyboard
    )

    logger.info(
        f'Пользователь {callback.from_user.id} вернулся в основное меню'
    )


@message_exception_handler(
    log_error_text='Ошибка при получении вопросов для'
)
@router.callback_query(F.data.in_(('get_faq', 'get_problems_with_products')))
async def get_questions(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Инлайн вывод общих вопросов и проблем с продуктами."""

    await callback.answer()

    question_type = (
        'GENERAL_QUESTIONS' if callback.data == 'get_faq'
        else 'PROBLEMS_WITH_PRODUCTS'
    )

    await callback.message.edit_text(
        bc.MESSAGE_FOR_GET_QUESTIONS,
        reply_markup=await faq_or_problems_with_products_inline_keyboard(
            question_type, session
        )
    )

    logger.info(
        f'Пользователь {callback.from_user.id} '
        f'запросил {question_type.lower()}.'
    )


@message_exception_handler(
    log_error_text='Ошибка при получении ответа на вопрос.'
)
@router.callback_query(F.data.startswith('answer:'))
async def get_faq_answer(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Вывод ответа на выбранный вопрос."""

    await callback.answer()

    question = await get_question_by_id(
        callback.data.split(':')[1], session
    )

    if question:
        await callback.message.edit_text(
            text=f'{question.answer}',
            reply_markup=InlineKeyboardBuilder().add(
                back_to_main_menu
            ).as_markup()
        )
    else:
        await callback.message.edit_text(bc.QUESTION_NOT_FOUND)

    logger.info(
        f'Пользователь {callback.from_user.id} запросил '
        f'ответ на вопрос {callback.data.split(':')[1]}'
    )


@message_exception_handler(
    log_error_text='Ошибка при возврате к выбору продуктов.'
)
@router.callback_query(F.data == 'back_to_previous_menu')
async def back_to_products(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Возвращает к выбору продуктов."""

    await callback.answer()

    await callback.message.edit_text(
        text=bc.MESSAGE_FOR_BACK_TO_PRODUCTS,
        reply_markup=await inline_products_and_services(session)
    )

    logger.info(
        f'Пользователь {callback.from_user.id} вернулся к выбору продуктов.'
    )


@message_exception_handler(
    log_error_text='Ошибка при запросе ответа для выбранной категории.'
)
@router.callback_query(F.data.startswith('category_'))
async def get_response_by_title(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Возвращает заготовленный ответ на выбранную категорию."""

    await callback.answer()

    category_id = int(callback.data.split('_')[1])

    await callback.message.edit_text(
        text=await response_text_by_id(category_id, session),
        reply_markup=await category_type_inline_keyboard(
            await get_title_by_id(category_id, session), session
        )
    )

    logger.info(
        f'Пользователь {callback.from_user.id} выбрал категорию {category_id}.'
    )


@message_exception_handler(
    log_error_text='Ошибка при показе портфолио.'
)
@router.callback_query(F.data == 'view_portfolio')
async def view_portfolio(callback: CallbackQuery) -> None:
    """Показ портфолио компании."""

    await callback.answer()

    await callback.message.edit_text(
        bc.MESSAGE_FOR_VIEW_PORTFOLIO,
        reply_markup=company_portfolio_choice
    )

    logger.info(f'Пользователь {callback.from_user.id} запросил портфолио.')


@message_exception_handler(
    log_error_text='Ошибка при запросе информации о компании.'
)
@router.callback_query(F.data == 'company_info')
async def company_info(callback: CallbackQuery) -> None:
    """Информация о компании."""

    await callback.answer()

    await callback.message.edit_text(
        bc.MESSAGE_FOR_COMPANY_INFO,
        reply_markup=company_information_keyboard
    )

    logger.info(
        f'Пользователь {callback.from_user.id} '
        f'запросил информацию о компании.'
    )


@message_exception_handler(
    log_error_text='Ошибка при запросе техподдержки.'
)
@router.callback_query(F.data == 'tech_support')
async def get_support(callback: CallbackQuery) -> None:
    """Выводит виды тех. поддержки."""

    await callback.answer()

    await callback.message.edit_text(
        bc.MESSAGE_FOR_GET_SUPPORT,
        reply_markup=support_keyboard
    )

    logger.info(f'Пользователь {callback.from_user.id} запросил техподдержку.')


@message_exception_handler(
    log_error_text='Ошибка при запросе информации о продуктах и услугах.'
)
@router.callback_query(F.data == 'products_services')
async def products_services(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Информация о продуктах и услугах."""

    await callback.answer()

    await callback.message.edit_text(
        bc.MESSAGE_FOR_PRODUCTS_SERVICES,
        reply_markup=await inline_products_and_services(session)
    )

    logger.info(
        f'Пользователь {callback.from_user.id} запросил '
        f'информацию о продуктах и услугах.'
    )
