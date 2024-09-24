from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyborads import (
    list_of_projects_keyboard, main_keyboard
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


@router.callback_query(F.data == 'get_faq')
async def get_faq(callback: CallbackQuery) -> None:
    """Инлайн вывод ответов на часто задаваемые вопросы."""

    pass
    # ( * ) кнопка с вопросами - ответ отдельным сообщением


@router.callback_query(F.data == 'get_problems_with_products')
async def get_problems_with_products(callback: CallbackQuery) -> None:
    """Инлайн вывод проблем с продуктами."""

    pass
    # ( * ) кнопка с вопросами - ответ отдельным сообщением


@router.callback_query(F.data == 'callback_request')
async def callback_request(callback: CallbackQuery) -> None:
    """Инлайн вывод запроса на обратный звонок."""

    pass
    # ( * )


@router.callback_data(F.data == 'back_to_products')
async def back_to_products(callback: CallbackQuery) -> None:
    """Возвращает к выюору продуктов."""

    pass
