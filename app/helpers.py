import logging
import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext

import bot.bot_const as bc
from bot.exceptions import message_exception_handler
from bot.keyborads import get_feedback_keyboard
from bot.bot_const import Form, FeedbackForm
from loggers.log import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


def get_user_id(message: Message | CallbackQuery) -> int:
    """Получает ID пользователя из сообщения."""

    return message.from_user.id


user_timers = {}


@message_exception_handler(
    log_error_text="Ошибка запуска таймера."
)
async def start_inactivity_timer(
    user_id: int, bot: Bot, timeout: int = 300
) -> None:
    """
    Запускает таймер.

    Для пользователя и отправляет сообщение, если пользователь бездействует.
    """

    logger.info(
        f"Запуск таймера для пользователя {user_id} с таймаутом {timeout}."
    )

    if user_id in user_timers:
        user_timers[user_id].cancel()

    user_timers[user_id] = asyncio.create_task(
        inactivity_timer(user_id, bot, timeout)
    )

    logger.info(f"Новый таймер запущен для пользователя {user_id}.")

    return None


@message_exception_handler(
    log_error_text="Ошибка периода бездействия и отправки сообщения."
)
async def inactivity_timer(user_id: int, bot: Bot, timeout: int):
    """Ожидания периода бездействия и отправки сообщения."""

    try:
        await asyncio.sleep(timeout)

        logger.info(f"Пользователь {user_id} неактивен. Отправка сообщения.")

        if user_id in user_timers:
            await bot.send_message(
                user_id, bc.MESSAGE_FOR_GET_FEEDBACK,
                reply_markup=get_feedback_keyboard
            )

            del user_timers[user_id]

            logger.info(
                f"Таймер для пользователя {user_id} удалён "
                f"после отправки сообщения."
            )

    except asyncio.CancelledError:
        logger.info(f"Таймер для пользователя {user_id} был отменён.")
        pass


@message_exception_handler(
    log_error_text="Ошибка при переходе к следующему вопросу."
)
async def ask_next_question(
    message: Message,
    state: FSMContext,
    next_state: State,
    questions: dict[FeedbackForm | Form, str],
) -> None:
    """Переход к следующему вопросу."""

    await state.set_state(next_state.state)
    await message.answer(questions[next_state])

    logger.info(f"Переход к следующему вопросу: {next_state}.")
