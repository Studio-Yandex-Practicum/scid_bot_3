import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyborads import (
    list_of_projects_keyboard, main_keyboard,
    faq_or_problems_with_products_inline_keyboard,
    category_type_inline_keyboard, inline_products_and_services,
    company_information_keyboard, company_portfolio_choice,
    support_keyboard, back_to_main_menu
)
from crud.questions import get_question_by_id
from crud.projects import get_title_by_id, response_text_by_id

router = Router()

logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'show_projects')
async def show_projects(callback: CallbackQuery):
    """Выводит список проектов компании."""

    await callback.answer()

    if callback.message:
        await callback.message.edit_text(
            'Вот некоторые из наших проектов. '
            'Выберите, чтобы узнать больше о каждом из них: ',
            reply_markup=await list_of_projects_keyboard()
        )

    # тут надо дописать блок else, если случилась ошибка
    # писать через (clause guard) ( * )


@router.callback_query(F.data == 'back_to_main_menu')
async def previous_choice(callback: CallbackQuery) -> None:
    """Возвращает в основное меню."""

    await callback.answer()

    if callback.message:
        await callback.message.edit_text(
            'Вы вернулись в оснвное меню. '
            'Как я могу помочь вам дальше? ',
            reply_markup=main_keyboard
        )
    # ( * )


@router.callback_query(F.data.in_(('get_faq', 'get_problems_with_products')))
async def get_questions(callback: CallbackQuery) -> None:
    """Инлайн вывод общих вопросов и проблем с продуктами."""

    await callback.answer()

    question_type = (
        'GENERAL_QUESTIONS' if callback.data == 'get_faq'
        else 'PROBLEMS_WITH_PRODUCTS'
    )

    if callback.message:
        await callback.message.edit_text(
            "Выберите вопрос:",
            reply_markup=await faq_or_problems_with_products_inline_keyboard(
                question_type
            )
        )


@router.callback_query(F.data.startswith('answer:'))
async def get_faq_answer(callback: CallbackQuery) -> None:
    """Вывод ответа на выбранный вопрос."""

    await callback.answer()

    question = await get_question_by_id(callback.data.split(':')[1])

    if question:
        await callback.message.edit_text(
            text=f"{question.answer}",
            reply_markup=InlineKeyboardBuilder().add(
                back_to_main_menu
            ).as_markup()
        )

    else:
        await callback.message.edit_text("Вопрос не найден.")


@router.callback_query(F.data == 'back_to_previous_menu')
async def back_to_products(callback: CallbackQuery) -> None:
    """Возвращает к выбору продуктов."""

    await callback.answer()

    if callback.message:

        await callback.message.edit_text(
            text='Вы вернулись к списку продуктов и услуг:',
            reply_markup=await inline_products_and_services()
        )


@router.callback_query(F.data.startswith('category_'))
async def get_response_by_title(callback: CallbackQuery) -> None:
    """Возвращает заготовленный ответ на выбранную категорию."""

    await callback.answer()

    if callback.message:

        category_id = int(callback.data.split('_')[1])

        await callback.message.edit_text(
            text=await response_text_by_id(category_id),
            reply_markup=await category_type_inline_keyboard(
                await get_title_by_id(category_id)
            )
        )


@router.callback_query(F.data == 'view_portfolio')
async def view_portfolio(callback: CallbackQuery) -> None:
    """Показ портфолио компании."""

    try:
        await callback.answer()

        await callback.message.edit_text(
            'Вот наше портфолио:',
            reply_markup=company_portfolio_choice
        )

        logger.info(f"Пользователь {callback.from_user.id} запросил портфолио")

    except Exception as e:
        logger.error(
            f"Ошибка при показе портфолио для "
            f"пользователя {callback.from_user.id}: {e}"
        )

        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == 'company_info')
async def company_info(callback: CallbackQuery) -> None:
    """Информация о компании."""

    try:
        await callback.answer()

        await callback.message.edit_text(
            'Информация о компании:',
            reply_markup=company_information_keyboard
        )

        logger.info(
            f"Пользователь {callback.from_user.id} "
            f"запросил информацию о компании"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при запросе информации о компании "
            f"для пользователя {callback.from_user.id}: {e}"
        )

        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == 'tech_support')
async def get_support(callback: CallbackQuery) -> None:
    """Выводит виды тех. поддержки."""

    await callback.answer()

    await callback.message.edit_text(
        'Какой вид технической поддержки вам нужен?',
        reply_markup=support_keyboard
    )


@router.callback_query(F.data == 'products_services')
async def products_services(callback: CallbackQuery) -> None:
    """Информация о продуктах и услугах."""

    try:
        await callback.message.edit_text(
            'Мы предлагаем следующие продукты и услуги. '
            'Какой из них вас интересует?',
            reply_markup=await inline_products_and_services()
        )
        await callback.answer()
        logger.info(
            f"Пользователь {callback.from_user.id} запросил "
            f"информацию о продуктах и услугах"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при запросе информации о продуктах и услугах "
            f"для пользователя {callback.from_user.id}: {e}"
        )

        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )
