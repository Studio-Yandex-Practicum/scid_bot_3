import logging

from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.validators import (
    is_valid_name, is_valid_phone_number, format_phone_number
)

router = Router()
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    """Форма для связи с менеджером."""

    first_name = State()
    last_name = State()
    middle_name = State()
    phone_number = State()


QUESTIONS = {
    Form.first_name: "Введите ваше имя:",
    Form.last_name: "Введите вашу фамилию:",
    Form.middle_name: (
        "Введите ваше отчество (или 'нет', если отсутствует):"
    ),
    Form.phone_number: (
        "Введите ваш номер телефона (в формате +7XXXXXXXXXX "
        "или 8XXXXXXXXXX):"
    )
}


@router.message(F.text == 'Связаться с менеджером.')
async def contact_with_manager(message: Message, state: FSMContext) -> None:
    """Выводит форму для связи с менеджером."""

    try:
        await message.answer(
            'Пожалуйста, оставьте ваше имя и контактный номер, '
            'и наш менеджер свяжется с вами.'
        )

        await ask_next_question(message, state, Form.first_name)

        logger.info(
            f"Пользователь {message.from_user.id} начал процесс."
        )

    except Exception as e:
        logger.error(
            f"Ошибка при выводе формы для пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")


async def ask_next_question(
        message: Message, state: FSMContext, next_state: State
) -> None:
    """Переход к следующему вопросу."""

    try:
        await state.set_state(next_state)
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
            await ask_next_question(message, state, Form.first_name)
            return

        await state.update_data(first_name=message.text)

        logger.info(
            f"Пользователь {message.from_user.id} ввёл имя: {message.text}"
        )

        await ask_next_question(message, state, Form.last_name)

    except Exception as e:
        logger.error(
            f"Ошибка при обработке имени пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")


@router.message(Form.last_name)
async def process_last_name(message: Message, state: FSMContext) -> None:
    """Состояние: ввод фамилии."""

    try:
        if not is_valid_name(message.text):
            await message.answer(
                "Фамилия должна содержать только буквы. Попробуйте снова."
            )
            await ask_next_question(message, state, Form.last_name)
            return

        await state.update_data(last_name=message.text)

        logger.info(
            f"Пользователь {message.from_user.id} ввёл фамилию: "
            f"{message.text}"
        )

        await ask_next_question(message, state, Form.middle_name)

    except Exception as e:
        logger.error(
            f"Ошибка при обработке фамилии пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")


@router.message(Form.middle_name)
async def process_middle_name(message: Message, state: FSMContext) -> None:
    """Состояние: ввод отчества."""

    try:
        if message.text.lower() != "нет" and not is_valid_name(message.text):
            await message.answer(
                "Отчество должно содержать только буквы или быть 'нет'. "
                "Попробуйте снова."
            )

            await ask_next_question(message, state, Form.middle_name)
            return

        await state.update_data(middle_name=message.text)

        logger.info(
            f"Пользователь {message.from_user.id} ввёл отчество: "
            f"{message.text}"
        )

        await ask_next_question(message, state, Form.phone_number)

    except Exception as e:
        logger.error(
            f"Ошибка при обработке отчества пользователя "
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

            await ask_next_question(message, state, Form.phone_number)
            return

        formatted_phone_number = format_phone_number(message.text)

        await state.update_data(phone_number=formatted_phone_number)

        logger.info(
            f"Пользователь {message.from_user.id} ввёл телефон: "
            f"{formatted_phone_number}"
        )

        user_data = await state.get_data()
        await message.answer(
            f"Форма заполнена!\n"
            f"Имя: {user_data['first_name']}\n"
            f"Фамилия: {user_data['last_name']}\n"
            f"Отчество: {user_data['middle_name']}\n"
            f"Номер телефона: {user_data['phone_number']}"
        )

        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(
            text="Вернуться в главное меню", callback_data="back_to_main_menu"
        ))

        await message.answer(
            "Вы можете вернуться в главное меню.",
            reply_markup=keyboard.as_markup()
        )

        await state.clear()

    except Exception as e:
        logger.error(
            f"Ошибка при обработке номера телефона пользователя "
            f"{message.from_user.id}: {e}"
        )

        await message.answer("Произошла ошибка. Попробуйте снова.")
