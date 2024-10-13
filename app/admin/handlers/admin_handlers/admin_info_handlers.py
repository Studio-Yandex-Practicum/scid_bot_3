from aiogram import F, Router
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.admin_managers import (
    QuestionCreateManager,
    QuestionUpdateManager,
    CreateQuestionStates,
    UpdateQuestionStates,
    QuestionDeleteManager,
    DeleteQuestionStates,
)
from admin.filters.filters import ChatTypeFilter, IsAdmin
from admin.handlers.admin_handlers.admin import SectionState
from admin.admin_settings import (
    ADMIN_BASE_OPTIONS,
    ADMIN_QUESTION_OPTIONS,
    SUPPORT_OPTIONS,
)

PROBLEMS_MENU = SUPPORT_OPTIONS.get("problems_with_products")
GENERAL_QEUSTIONS_MENU = SUPPORT_OPTIONS.get("general_questions")


info_router = Router()
info_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

question_create_manager = QuestionCreateManager()
question_update_manager = QuestionUpdateManager()
question_delete_manager = QuestionDeleteManager()


@info_router.callback_query(
    or_f(SectionState.general_questions, SectionState.problems_with_products),
    F.data == ADMIN_BASE_OPTIONS.get("create"),
)
async def add_question(callback: CallbackQuery, state: FSMContext):
    await question_create_manager.add_question_text(callback, state)


@info_router.message(CreateQuestionStates.question, F.text)
async def add_question_text(message: Message, state: FSMContext):
    await question_create_manager.add_answer_text(message, state)


@info_router.message(CreateQuestionStates.answer, F.text)
async def add_question_answer(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    await question_create_manager.add_question_to_db(message, state, session)


@info_router.callback_query(
    or_f(SectionState.general_questions, SectionState.problems_with_products),
    F.data == ADMIN_BASE_OPTIONS.get("delete"),
)
async def question_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await question_delete_manager.select_question(
        callback,
        state,
        next_state=DeleteQuestionStates.select,
        session=session,
    )


@info_router.callback_query(
    DeleteQuestionStates.select,
    and_f(F.data != PROBLEMS_MENU, F.data != GENERAL_QEUSTIONS_MENU),
)
async def confirm_delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await question_delete_manager.confirm_delete(callback, state, session)


@info_router.callback_query(
    DeleteQuestionStates.confirm,
    and_f(F.data != PROBLEMS_MENU, F.data != GENERAL_QEUSTIONS_MENU),
)
async def delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await question_delete_manager.delete_question(callback, state, session)


@info_router.callback_query(
    or_f(SectionState.general_questions, SectionState.problems_with_products),
    F.data == ADMIN_BASE_OPTIONS.get("update"),
)
async def update_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await question_update_manager.select_question(
        callback,
        state,
        next_state=UpdateQuestionStates.select,
        session=session,
    )


@info_router.callback_query(
    UpdateQuestionStates.select,
    and_f(
        F.data != ADMIN_QUESTION_OPTIONS.get("question"),
        F.data != ADMIN_QUESTION_OPTIONS.get("answer"),
        F.data != PROBLEMS_MENU,
        F.data != GENERAL_QEUSTIONS_MENU,
    ),
)
async def update_question_choice(
    callback: CallbackQuery, session: AsyncSession
):
    await question_update_manager.update_data_type(callback, session)


@info_router.callback_query(
    UpdateQuestionStates.select,
    F.data == ADMIN_QUESTION_OPTIONS.get("question"),
)
async def update_question_text(callback: CallbackQuery, state: FSMContext):
    await question_update_manager.update_question(callback, state)


@info_router.callback_query(
    UpdateQuestionStates.select, F.data == ADMIN_QUESTION_OPTIONS.get("answer")
)
async def update_question_answer(callback: CallbackQuery, state: FSMContext):
    await question_update_manager.update_answer(callback, state)


@info_router.message(
    or_f(UpdateQuestionStates.question, UpdateQuestionStates.answer), F.text
)
async def update_question_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    await question_update_manager.update_question_in_db(
        message, state, session
    )
