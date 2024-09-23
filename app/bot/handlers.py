from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyborads import (
    main_keyboard, company_information_keyboard,
    inline_products_and_services, company_portfolio_choice,
    support_keyboard
)


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Выводит приветствие пользователя."""

    await message.answer(
        'Здравстуйте! Я ваш виртуальный помошник.'
        'Как я могу помочь вам сегодня?',
        reply_markup=main_keyboard
    )


@router.message(F.text == 'Посмотреть портфолио.')
async def view_profile(message: Message) -> None:
    """Выводит портфолио компании."""

    await message.answer(
        'Вот ссылка на на наше портофолио: [здесь url]. '
        'Хотите узнать больше о конкретных проектах '
        'или услугах?',
        reply_markup=company_portfolio_choice
    )


@router.message(F.text == 'Получить информацию о компании.')
async def get_information_about_company(message: Message) -> None:
    """Выводит информацию о компнии."""

    await message.answer(
        'Вот несколько вариантов информации о нашей '
        'компании. Что именно вас интересует? ',
        reply_markup=company_information_keyboard
    )


@router.message(F.text == 'Узнать о продуктах и услугах.')
async def get_information_about_products_and_services(
    message: Message
) -> None:
    """Выводит информация о продуктах и услугах."""

    await message.answer(
        'Мы предлагаем следующие продукты и услуги.'
        'Какой из низ вас интересует?',
        reply_markup=await inline_products_and_services()
    )


@router.message(F.text == 'Получить техническую поддержку.')
async def get_support(message: Message) -> None:
    """Выводит виды тех. поддержки."""

    await message.answer(
        'Какой вид технической поддержки '
        'вам нужен? ',
        reply_markup=support_keyboard
    )
