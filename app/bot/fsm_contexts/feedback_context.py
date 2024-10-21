import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import bot.bot_const as bc
from bot.exceptions import message_exception_handler
from helpers import ask_next_question, get_user_id
from loggers.log import setup_logging
from bot.validators import is_valid_rating
from crud import user_crud, feedback_crud
from bot.keyborads import get_back_to_main_keyboard


router = Router()

setup_logging()
logger = logging.getLogger(__name__)


@message_exception_handler(log_error_text="Ошибка при составлении фидбека.")
@router.callback_query(F.data == "get_feedback_yes")
async def get_feedback_yes(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    """Начало сбора обратной связи."""

    user_id = get_user_id(callback)

    user = await user_crud.get_user_by_tg_id(user_id, session)

    await state.update_data(user=user.id)

    await ask_next_question(
        callback.message, state, bc.FeedbackForm.rating, bc.FEEDBACK_QUESTIONS
    )

    logger.info(f"Пользователь {callback.from_user.id} начал процесс.")


@message_exception_handler(log_error_text="Ошибка при обработке оценки.")
@router.message(bc.FeedbackForm.rating)
async def process_rating(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    """Обрабатывает ввод оценки."""

    rating = message.text

    if not is_valid_rating(rating):
        await message.answer("Пожалуйста, введите число от 1 до 10.")
        return

    await state.update_data(rating=int(rating))

    await ask_next_question(
        message, state, bc.FeedbackForm.feedback_text, bc.FEEDBACK_QUESTIONS
    )

    logger.info(f"Пользователь {message.from_user.id} ввел оценку.")


@message_exception_handler(log_error_text="Ошибка при обработке текста.")
@router.message(bc.FeedbackForm.feedback_text)
async def process_description(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    """Обрабатывает комментарий пользователя."""

    await state.update_data(feedback_text=message.text)

    logger.info(f"Пользователь {message.from_user.id} ввел текст.")

    feedback_data = await state.get_data()

    await feedback_crud.create(feedback_data, session)

    logger.info(f'Запись создана в БД с ID: {feedback_data.get("user")}.')

    await message.answer(
        f"Спасибо за вашу оценку: {feedback_data['rating']}\n"
        f"Ваш комментарий: {feedback_data['feedback_text']}",
        reply_markup=await get_back_to_main_keyboard(),
    )

    await state.clear()
