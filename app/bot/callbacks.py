from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyborads import (
    list_of_projects_keyboard, main_keyboard,
    faq_or_problems_with_products_inline_keyboard
)
from crud.request_to_manager import (
    get_question_by_id, response_text_by_id,
    get_question_by_title
)


router = Router()


@router.callback_query(F.data == 'show_projects')
async def show_projects(callback: CallbackQuery):
    """Выводит список проектов компании."""

    await callback.answer()

    if callback.message:
        await callback.message.answer(
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
        await callback.message.answer(
            'Вы вернулись в оснвное меню. '
            'Как я могу помочь вам дальше? ',
            reply_markup=main_keyboard
        )
    # ( * )


@router.callback_query(F.data.in_(['get_faq', 'get_problems_with_products']))
async def get_questions(callback: CallbackQuery) -> None:
    """Инлайн вывод общих вопросов и проблем с продуктами."""

    await callback.answer()

    question_type = (
        'GENERAL_QUESTIONS' if callback.data == 'get_faq'
        else 'PROBLEMS_WITH_PRODUCTS'
    )

    # Получаем клавиатуру с вопросами
    keyboard = await faq_or_problems_with_products_inline_keyboard(question_type)

    if callback.message:
        await callback.message.answer(
            "Выберите вопрос:",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith('answer:'))
async def get_faq_answer(callback: CallbackQuery) -> None:
    """Вывод ответа на выбранный вопрос."""

    await callback.answer()

    question_id = int(callback.data.split(':')[1])
    question = await get_question_by_id(question_id)

    if question:
        await callback.message.answer(f"{question.answer}")
    else:
        await callback.message.answer("Вопрос не найден.")


@router.callback_query(F.data == 'callback_request')
async def callback_request(callback: CallbackQuery) -> None:
    """Инлайн вывод запроса на обратный звонок."""

    pass

    # ( * )


@router.callback_query(F.data == 'back_to_products')
async def back_to_products(callback: CallbackQuery) -> None:
    """Возвращает к выбору продуктов."""

    pass


@router.callback_query(F.data.startswith('category_'))
async def get_response_by_title(callback: CallbackQuery) -> None:
    """Возвращает заготовленный ответ на выбранную категорию."""

    await callback.answer()

    if callback.message:

        category_id = int(callback.data.split('_')[1])

        await callback.message.answer(
            await response_text_by_id(category_id)
        )
