from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from bot.keyborads import (
    main_keyboard, company_information_keyboard,
    inline_products_and_services
)


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Приветствие пользователя."""

    await message.answer(
        'Здравстуйте! Я ваш виртуальный помошник.'
        'Как я могу помочь вам сегодня?',
        reply_markup=main_keyboard
    )


@router.message(F.text == 'Посмотреть портфолио.')
async def view_profile(message: Message) -> None:
    """Портфолио компании."""

    await message.answer(
        'Вот ссылка на на наше портофолио: [здесь url]. '
        'Хотите узнать больше о конкретных проектах '
        'или услугах?'
    )


@router.message(F.text == 'Получить информацию о компании.')
async def get_information_about_company(message: Message) -> None:
    """Информация о компнии."""

    await message.answer(
        'Вот несколько вариантов информации о нашей '
        'компании. Что именно вас интересует? ',
        reply_markup=company_information_keyboard
    )


@router.message(F.text == 'Узнать о продуктах и услугах.')
async def get_information_about_products_and_services(message: Message) -> None:
    """Информация о продуктах и услугах."""

    await message.answer(
        'Мы предлагаем следующие продукты и услуги.'
        'Какой из низ вас интересует?',
        reply_markup=await inline_products_and_services()
    )


@router.callback_query(lambda call: call == 'previous_choice')
def previous_choice(callback_query: CallbackQuery) -> None:
    pass
