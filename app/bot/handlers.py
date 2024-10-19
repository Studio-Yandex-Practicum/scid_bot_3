import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.keyboards.keyboards import get_inline_keyboard
from admin.admin_settings import MAIN_MENU_BUTTONS
from bot.bot_const import (
    ADMIN_NEGATIVE_ANSWER, ADMIN_POSITIVE_ANSWER, START_MESSAGE
)
from models.models import RoleEnum
from crud.users import create_user_id, get_role_by_tg_id, is_user_in_db
from bot.keyborads import main_keyboard
from bot.exceptions import message_exception_handler
from helpers import get_user_id, start_inactivity_timer
from core.bot_setup import bot
from bot.bot_const import MESSAGE_FOR_NOT_SUPPORTED_CONTENT_TYPE
from loggers.log import setup_logging


router = Router()


setup_logging()
logger = logging.getLogger(__name__)


@message_exception_handler(
    log_error_text="Ошибка при обработке команды /admin."
)
@router.message(Command("admin"))
async def cmd_admin(message: Message, session: AsyncSession) -> None:
    """Вход в админку."""

    user_id = get_user_id(message)
    role = await get_role_by_tg_id(user_id, session)

    if role in (RoleEnum.ADMIN, RoleEnum.MANAGER):
        await message.answer(
            ADMIN_POSITIVE_ANSWER,
            reply_markup=await get_inline_keyboard(MAIN_MENU_BUTTONS),
        )
    else:
        await message.answer(ADMIN_NEGATIVE_ANSWER)

    logger.info(f"Пользователь {user_id} вызвал команду /admin.")


@message_exception_handler(
    log_error_text="Ошибка при обработке команды /start."
)
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Выводит приветствие пользователя."""

    await state.clear()

    user_id = get_user_id(message)

    if not await is_user_in_db(user_id, session):
        await create_user_id(user_id, session)

    await message.answer(START_MESSAGE, reply_markup=main_keyboard)

    logger.info(f"Пользователь {user_id} вызвал команду /start.")

    await start_inactivity_timer(message, user_id, bot)


@router.message(F.content_type)
async def handle_any_content(message: Message):
    """Ответ на любой другой тип контента."""

    await message.answer(MESSAGE_FOR_NOT_SUPPORTED_CONTENT_TYPE)
