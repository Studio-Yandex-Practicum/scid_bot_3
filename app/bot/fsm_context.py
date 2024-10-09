import logging

from aiogram import F, Router
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyborads import back_to_main_menu
from crud.request_to_manager import create_request_to_manager
from bot.validators import (
    is_valid_name, is_valid_phone_number, format_phone_number
)
import bot.bot_const as bc
from bot.exceptions import message_exception_handler


router = Router()
logger = logging.getLogger(__name__)


@message_exception_handler(
    log_error_text='Ошибка при выводе формы.'
)
@router.callback_query(F.data.in_(('contact_manager', 'callback_request')))
async def contact_with_manager(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Выводит форму для связи с менеджером или запрос на обратный звонок."""

    await state.update_data(request_type=callback.data)

    await callback.message.edit_text(bc.START_INPUT_USER_DATA)

    await ask_next_question(callback.message, state, bc.Form.first_name)

    logger.info(f'Пользователь {callback.from_user.id} начал процесс.')


@message_exception_handler(
    log_error_text='Ошибка при переходе к следующему вопросу.'
)
async def ask_next_question(
    message: Message, state: FSMContext, next_state: State
) -> None:
    """Переход к следующему вопросу."""

    await state.set_state(next_state.state)
    await message.answer(bc.QUESTIONS[next_state])

    logger.info(f'Переход к следующему вопросу: {next_state}.')


@message_exception_handler(
    log_error_text='Ошибка при обработке имени пользователя.'
)
@router.message(bc.Form.first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    """Состояние: ввод имени."""

    if not is_valid_name(message.text):
        await message.answer(bc.INPUT_NAME)
        return

    await state.update_data(first_name=message.text)

    logger.info(
        f'Пользователь {message.from_user.id} ввёл имя: {message.text}.'
    )

    await ask_next_question(message, state, bc.Form.phone_number)


@message_exception_handler(
    log_error_text='Ошибка при обработке номера телефона пользователя.'
)
@router.message(bc.Form.phone_number)
async def process_phone_number(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    """Состояние: ввод номера телефона."""

    if not is_valid_phone_number(message.text):
        await message.answer(bc.INPUT_NUMBER_PHONE)
        return

    formatted_phone_number = format_phone_number(message.text)

    await state.update_data(phone_number=formatted_phone_number)

    logger.info(
        f'Пользователь {message.from_user.id} ввёл телефон: '
        f'{formatted_phone_number}.'
    )

    user_data = await state.get_data()
    request_type = user_data.pop('request_type')

    new_request = await create_request_to_manager(
        user_data, request_type, session
    )

    logger.info(f'Запись создана в БД с ID: {new_request.id}.')

    await message.answer(
        bc.succses_answer(user_data),
        reply_markup=InlineKeyboardBuilder().add(
            back_to_main_menu
        ).as_markup()
    )

    await state.clear()
