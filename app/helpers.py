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


async def start_inactivity_timer(
    user_id: int, bot: Bot, timeout: int = 10
) -> None:
    """
    Запускает таймер.

    Для пользователя и отправляет сообщение, если пользователь бездействует.
    """

    if user_id in user_timers:
        user_timers[user_id].cancel()

    user_timers[user_id] = asyncio.create_task(
        inactivity_timer(user_id, bot, timeout)
    )

    return None


async def inactivity_timer(user_id: int, bot: Bot, timeout: int):
    """Ожидания периода бездействия и отправки сообщения."""

    try:
        await asyncio.sleep(timeout)

        if user_id in user_timers:
            await bot.send_message(
                user_id, bc.MESSAGE_FOR_GET_FEEDBACK,
                reply_markup=get_feedback_keyboard
            )
            del user_timers[user_id]

    except asyncio.CancelledError:
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
