from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery, Message

from crud.info_crud import info_crud
from admin.filters.filters import ChatTypeFilter, IsAdmin
from admin.handlers.admin_handlers.admin import SectionState
from admin.keyboards.keyboards import (
    get_inline_confirmation,
    get_inline_keyboard,
)

from admin.admin_settings import SUPPORT_OPTIONS
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup

info_router = Router()
info_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class AddQuestion(StatesGroup):
    question = State()
    answer = State()
    question_type = State()


class UpdateQuestion(StatesGroup):
    question = State()
    answer = State()
    question_type = State()
    confirm = State()


class DeleteQuestion(AddQuestion):
    confirm = State()


PREVIOUS_MENU = SUPPORT_OPTIONS.get("faq")


async def set_question_type(state: str):
    question_type = state.split(":")[-1]
    return SUPPORT_OPTIONS.get(question_type)


async def get_question_list(question_type: str, session: AsyncSession):
    return [
        question.question
        for question in await info_crud.get_all_questions_by_type(
            question_type, session
        )
    ]


@info_router.callback_query(
    or_f(SectionState.faq, SectionState.troubleshooting), F.data == "Добавить"
)
async def add_question(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.set_state(AddQuestion.question_type)
    await state.update_data(
        question_type=await set_question_type(current_state)
    )
    await callback.message.answer("Введите текст нового вопрос")
    await state.set_state(AddQuestion.question)


@info_router.message(AddQuestion.question, F.text)
async def add_question_text(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Введите ответ на этот вопрос")
    print(await state.get_data())
    await state.set_state(AddQuestion.answer)


@info_router.message(AddQuestion.answer, F.text)
async def add_question_answer(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    await state.update_data(answer=message.text)
    data = await state.get_data()
    await info_crud.create(data, session=session)
    await message.answer(
        "Вопрос добавлен!",
        reply_markup=await get_inline_keyboard(
            previous_menu=data.get("question_type")
        ),
    )
    await state.clear()


@info_router.callback_query(
    or_f(SectionState.faq, SectionState.troubleshooting), F.data == "Удалить"
)
async def question_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    current_state = await state.get_state()
    await state.set_state(DeleteQuestion.question_type)
    await state.update_data(
        question_type=await set_question_type(current_state)
    )
    question_type = (await state.get_data()).get("question_type")
    question_list = await get_question_list(question_type, session)
    await callback.message.edit_text(
        "Какой вопрос удалить?",
        reply_markup=await get_inline_keyboard(
            question_list, previous_menu=PREVIOUS_MENU
        ),
    )
    await state.set_state(DeleteQuestion.question)


@info_router.callback_query(DeleteQuestion.question, F.data)
async def confirm_delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    question = await info_crud.get_by_string(callback.data, session)
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить этот вопрос?\n\n {question.question}",
        reply_markup=await get_inline_confirmation(
            option=question.question, cancel_option=PREVIOUS_MENU
        ),
    )
    await state.set_state(DeleteQuestion.confirm)


@info_router.callback_query(DeleteQuestion.confirm, F.data != PREVIOUS_MENU)
async def delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.clear()
    question = await info_crud.get_by_string(callback.data, session)
    await info_crud.remove(question, session)
    await callback.message.edit_text(
        "Вопрос удален!",
        reply_markup=await get_inline_keyboard(
            previous_menu=question.question_type
        ),
    )


@info_router.callback_query(
    or_f(SectionState.faq, SectionState.troubleshooting),
    F.data == "Изменить",
)
async def update_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    current_state = await state.get_state()
    await state.set_state(UpdateQuestion.question_type)
    await state.update_data(
        question_type=await set_question_type(current_state)
    )
    question_type = (await state.get_data()).get("question_type")
    question_list = await get_question_list(question_type, session)
    await callback.message.edit_text(
        "Какой вопрос отредактировать?",
        reply_markup=await get_inline_keyboard(
            question_list, previous_menu=PREVIOUS_MENU
        ),
    )
    await state.set_state(UpdateQuestion.question)


@info_router.callback_query(
    UpdateQuestion.question, and_f(F.data != "Вопрос", F.data != "Ответ")
)
async def update_question_choice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(question=callback.data)
    await callback.message.answer(
        "Что вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            ["Вопрос", "Ответ"], previous_menu=PREVIOUS_MENU
        ),
    )


@info_router.callback_query(UpdateQuestion.question, F.data == "Вопрос")
async def update_question_text(callback: CallbackQuery, state: FSMContext):
    question_text = (await state.get_data()).get("question")
    await callback.message.answer(
        f"Сейчас вопрос записан вот так:\n\n{question_text}\n\n Введите новый текст"
    )
    await state.set_state(UpdateQuestion.confirm)


@info_router.callback_query(UpdateQuestion.question, F.data == "Ответ")
async def update_question_answer(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    question_text = (await state.get_data()).get("question")
    answer = await info_crud.get_by_string(question_text, session)
    await callback.message.answer(
        f"Сейчас ответ записан вот так:\n\n{answer.answer}\n\n Введите новый текст"
    )
    await state.set_state(UpdateQuestion.answer)


@info_router.message(
    or_f(UpdateQuestion.confirm, UpdateQuestion.answer), F.text
)
async def update_question_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    current_state = await state.get_state()
    old_data = await state.get_data()
    question = await info_crud.get_by_string(old_data.get("question"), session)

    if current_state == UpdateQuestion.confirm:
        await state.update_data(question=message.text)
    elif current_state == UpdateQuestion.answer:
        await state.update_data(answer=message.text)

    updated_data = await state.get_data()
    await info_crud.update(question, updated_data, session=session)
    await message.answer(
        "Вопрос обновлен!",
        reply_markup=await get_inline_keyboard(
            previous_menu=updated_data.get("question_type")
        ),
    )
    await state.clear()
