import logging
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message


from bot.keyborads import (
    main_keyboard, company_information_keyboard,
    inline_products_and_services, company_portfolio_choice,
)

router = Router()

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Выводит приветствие пользователя."""

    try:
        await message.answer(
            'Здравстуйте! Я ваш виртуальный помощник. '
            'Как я могу помочь вам сегодня?',
            reply_markup=main_keyboard
        )

        logger.info(
            f"Пользователь {message.from_user.id} вызвал команду /start"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при обработке команды /start для пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )


@router.message(F.text == 'Посмотреть портфолио.')
async def view_portfolio(message: Message) -> None:
    """Показ портфолио компании."""

    try:
        await message.answer(
            'Вот наше портфолио:',
            reply_markup=company_portfolio_choice
        )
        logger.info(
            f"Пользователь {message.from_user.id} запросил портфолио"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при показе портфолио для пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )


@router.message(F.text == 'Получить информацию о компании.')
async def company_info(message: Message) -> None:
    """Информация о компании."""

    try:
        await message.answer(
            'Информация о компании:',
            reply_markup=company_information_keyboard
        )

        logger.info(
            f"Пользователь {message.from_user.id} запросил информацию "
            f"о компании"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при запросе информации о компании для пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )


@router.message(F.text == 'Узнать о продуктах и услугах.')
async def products_services(message: Message) -> None:
    """Информация о продуктах и услугах."""

    try:
        await message.answer(
            'Вот наши продукты и услуги:',
            reply_markup=await inline_products_and_services()
        )

        logger.info(
            f"Пользователь {message.from_user.id} запросил информацию "
            f"о продуктах и услугах"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при запросе информации о продуктах и услугах "
            f"для пользователя {message.from_user.id}: {e}"
        )

        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )
