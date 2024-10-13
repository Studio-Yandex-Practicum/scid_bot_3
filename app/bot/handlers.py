import logging
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.admin.keyboards.keyboards import get_inline_keyboard
from app.const import MAIN_MENU_BUTTONS
from app.bot.bot_const import (
    ADMIN_NEGATIVE_ANSWER, ADMIN_POSITIVE_ANSWER, START_MESSAGE
)
from app.models.models import RoleEnum
from app.crud.users import (
    create_user_id, get_role_by_tg_id, is_user_in_db
)
from app.bot.keyborads import main_keyboard
from app.bot.exceptions import message_exception_handler
from app.helpers import get_user_id

router = Router()

logger = logging.getLogger(__name__)


@message_exception_handler(
    log_error_text='Ошибка при обработке команды /admin.'
)
@router.message(Command('admin'))
async def cmd_admin(message: Message, session: AsyncSession, bot: Bot) -> None:
    """Вход в админку."""

    user_id = get_user_id(message)
    role = await get_role_by_tg_id(user_id, session)

    if role in (RoleEnum.ADMIN, RoleEnum.MANAGER):
        await bot.send_message(
            chat_id=message.chat.id,
            text=ADMIN_POSITIVE_ANSWER,
            reply_markup=await get_inline_keyboard(MAIN_MENU_BUTTONS)
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=ADMIN_NEGATIVE_ANSWER
        )

    logger.info(
        f'Пользователь {user_id} вызвал команду /admin.'
    )


@message_exception_handler(
    log_error_text='Ошибка при обработке команды /start.'
)
@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot) -> None:
    """Выводит приветствие пользователя."""

    user_id = get_user_id(message)

    if not await is_user_in_db(user_id, session):
        await create_user_id(user_id, session)

    await bot.send_message(
        chat_id=message.chat.id,
        text=START_MESSAGE,
        reply_markup=main_keyboard
    )

    logger.info(
        f'Пользователь {user_id} вызвал команду /start.'
    )
