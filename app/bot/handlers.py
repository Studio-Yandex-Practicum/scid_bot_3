import logging
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from models.models import RoleEnum
from crud.users import (
    create_user_id, get_role_by_tg_id, is_user_in_db
)
from bot.keyborads import (
    main_keyboard
)

router = Router()

logger = logging.getLogger(__name__)


# TODO: данные из message нужно достать один раз,
# сейчас в каждой фукнции дергаем

@router.message(Command('admin'))
async def cmd_admin(message: Message) -> None:
    """Вход в админку."""

    role = await get_role_by_tg_id(message.from_user.id)

    response = 'Добро пожаловать в админку' if role in (
        RoleEnum.ADMIN, RoleEnum.MANAGER
    ) else '403: Forbidden'

    await message.answer(response)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Выводит приветствие пользователя."""

    if not await is_user_in_db(message.from_user.id):
        await create_user_id(message.from_user.id)

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
