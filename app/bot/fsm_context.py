from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


class Form(StatesGroup):
    """Форма для связи с менеджером."""

    first_name = State()
    last_name = State()
    middle_name = State()
    phone_number = State()


QUESTIONS = {
    Form.first_name: "Введите ваше имя:",
    Form.last_name: "Введите вашу фамилию:",
    Form.middle_name: "Введите ваше отчество (или 'нет', если отсутствует):",
    Form.phone_number: "Введите ваш номер телефона:"
}


@router.message(F.text == 'Связаться с менеджером.')
async def contact_with_manager(message: Message, state: FSMContext) -> None:
    """Выводит связь с менеджером."""

    await message.answer(
        'Пожалуйста, оставьте ваше имя и '
        'контактный номер, и наш менеджер '
        'свяжется с вами.'
    )

    await ask_next_question(message, state, Form.first_name)


async def ask_next_question(
        message: Message, state: FSMContext, next_state: State
):
    await state.set_state(next_state)
    await message.answer(QUESTIONS[next_state])


@router.message(Form.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await ask_next_question(message, state, Form.last_name)


@router.message(Form.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await ask_next_question(message, state, Form.middle_name)


@router.message(Form.middle_name)
async def process_middle_name(message: Message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    await ask_next_question(message, state, Form.phone_number)


@router.message(Form.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)

    user_data = await state.get_data()
    await message.answer(
        f"Форма заполнена!\n"
        f"Имя: {user_data['first_name']}\n"
        f"Фамилия: {user_data['last_name']}\n"
        f"Отчество: {user_data['middle_name']}\n"
        f"Номер телефона: {user_data['phone_number']}"
    )  # вынести кнопку выхода в главное меню и добавить ее тут

    await state.clear()
