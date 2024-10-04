import logging

from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyborads import back_to_main_menu
from crud.request_to_manager import create_request_to_manager
from bot.validators import (
    is_valid_name, is_valid_phone_number, format_phone_number
)

router = Router()
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    """Форма для связи с менеджером."""

    first_name = State()
    phone_number = State()


QUESTIONS = {
    Form.first_name: "Введите ваше имя:",
    Form.phone_number: (
        "Введите ваш номер телефона (в формате +7XXXXXXXXXX "
        "или 8XXXXXXXXXX):"
    )
}


@router.callback_query(F.data.in_(('contact_manager', 'callback_request')))
async def contact_with_manager(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Выводит форму для связи с менеджером или запрос на обратный звонок."""

    try:

        await state.update_data(request_type=callback.data)

        await callback.message.edit_text(
            'Пожалуйста, оставьте ваше имя и контактный номер, '
            'и наш менеджер свяжется с вами.'
        )

        await ask_next_question(callback.message, state, Form.first_name)

        logger.info(
            f"Пользователь {callback.from_user.id} начал процесс."
        )

    except Exception as e:
        logger.error(
            f"Ошибка при выводе формы для пользователя "
            f"{callback.from_user.id}: {e}"
        )

        await callback.message.answer("Произошла ошибка. Попробуйте снова.")


async def ask_next_question(
        message: Message, state: FSMContext, next_state: State
) -> None:
    """Переход к следующему вопросу."""

    try:
        await state.set_state(next_state.state)
        await message.answer(QUESTIONS[next_state])
        logger.info(
            f"Переход к следующему вопросу: {next_state}"
        )

    except Exception as e:
        logger.error(
            f"Ошибка при переходе к следующему вопросу для пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")


@router.message(Form.first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    """Состояние: ввод имени."""

    try:
        if not is_valid_name(message.text):
            await message.answer(
                "Имя должно содержать только буквы. Попробуйте снова."
            )
            return

        await state.update_data(first_name=message.text)

        logger.info(
            f"Пользователь {message.from_user.id} ввёл имя: {message.text}"
        )

        await ask_next_question(message, state, Form.phone_number)

    except Exception as e:
        logger.error(
            f"Ошибка при обработке имени пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")


@router.message(Form.phone_number)
async def process_phone_number(message: Message, state: FSMContext) -> None:
    """Состояние: ввод номера телефона."""

    try:
        if not is_valid_phone_number(message.text):
            await message.answer(
                "Номер телефона должен быть в формате +7XXXXXXXXXX "
                "или 8XXXXXXXXXX. Попробуйте снова."
            )
            return

        formatted_phone_number = format_phone_number(message.text)

        await state.update_data(phone_number=formatted_phone_number)

        logger.info(
            f"Пользователь {message.from_user.id} ввёл телефон: "
            f"{formatted_phone_number}"
        )

        user_data = await state.get_data()
        request_type = user_data.pop('request_type')

        new_request = await create_request_to_manager(user_data, request_type)

        logger.info(f"Запись создана в БД с ID: {new_request.id}")

        await message.answer(
            f'Спасибо! Наш менеджер свяжется '
            f'с вами в ближайшее время.\n'
            f"Отправленная форма:\n"
            f"Имя: {user_data['first_name']}\n"
            f"Номер телефона: {user_data['phone_number']}",
            reply_markup=InlineKeyboardBuilder().add(
                back_to_main_menu)
            .as_markup()
        )

        await state.clear()

    except Exception as e:
        logger.error(
            f"Ошибка при обработке номера телефона пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")
