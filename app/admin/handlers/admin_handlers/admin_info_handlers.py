import logging

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
from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.handlers.admin_handlers.admin import SectionState
from admin.admin_settings import (
    ADMIN_BASE_OPTIONS,
    ADMIN_QUESTION_OPTIONS,
    SUPPORT_OPTIONS,
)
from bot.exceptions import message_exception_handler

logger = logging.getLogger(__name__)

PROBLEMS_MENU = SUPPORT_OPTIONS.get("problems_with_products")
GENERAL_QEUSTIONS_MENU = SUPPORT_OPTIONS.get("general_questions")


info_router = Router()
info_router.message.filter(ChatTypeFilter(["private"]), IsManagerOrAdmin())
info_router.callback_query.filter(IsManagerOrAdmin())

question_create_manager = QuestionCreateManager()
question_update_manager = QuestionUpdateManager()
question_delete_manager = QuestionDeleteManager()


@message_exception_handler(log_error_text='Ошибка при добавлении вопроса')
@info_router.callback_query(
    or_f(SectionState.general_questions, SectionState.problems_with_products),
    F.data == ADMIN_BASE_OPTIONS.get("create"),
)
async def add_question(callback: CallbackQuery, state: FSMContext):
    """Добавить вопрос."""
    await question_create_manager.add_question_text(callback, state)
    logger.info(f'Пользователь {callback.from_user.id} добавил новый вопрос.')


@message_exception_handler(
    log_error_text='Ошибка при добавлении текста вопроса'
)
@info_router.message(CreateQuestionStates.question, F.text)
async def add_question_text(message: Message, state: FSMContext):
    """Добавить текст вопроса."""
    await question_create_manager.add_answer_text(message, state)
    logger.info(f'Пользователь {message.from_user.id} добавил текст вопроса.')


@message_exception_handler(
    log_error_text='Ошибка при добавлении ответа на вопрос'
)
@info_router.message(CreateQuestionStates.answer, F.text)
async def add_question_answer(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    """Добавить ответ на вопрос в БД."""
    await question_create_manager.add_question_to_db(message, state, session)
    logger.info(
        f'Пользователь {message.from_user.id} добавил ответ на вопрос в БД.'
    )


@message_exception_handler(
    log_error_text='Ошибка при выборе вопроса для удаления'
)
@info_router.callback_query(
    or_f(SectionState.general_questions, SectionState.problems_with_products),
    F.data == ADMIN_BASE_OPTIONS.get("delete"),
)
async def question_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Запустить процесс выбора вопроса для удаления."""
    await question_delete_manager.select_question(
        callback,
        state,
        next_state=DeleteQuestionStates.select,
        session=session,
    )
    logger.info(
        f'Пользователь {callback.from_user.id} выбрал вопрос для удаления.'
    )


@message_exception_handler(
    log_error_text='Ошибка при подтверждении удаления вопроса'
)
@info_router.callback_query(
    DeleteQuestionStates.select,
    and_f(F.data != PROBLEMS_MENU, F.data != GENERAL_QEUSTIONS_MENU),
)
async def confirm_delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтвердить удаление вопроса."""
    await question_delete_manager.confirm_delete(callback, state, session)
    logger.info(
        f'Пользователь {callback.from_user.id} подтвердил удаление вопроса.'
    )


@message_exception_handler(log_error_text='Ошибка при удалении вопроса из БД')
@info_router.callback_query(
    DeleteQuestionStates.confirm,
    and_f(F.data != PROBLEMS_MENU, F.data != GENERAL_QEUSTIONS_MENU),
)
async def delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить вопрос из базы данных."""
    await question_delete_manager.delete_question(callback, state, session)
    logger.info(f'Пользователь {callback.from_user.id} удалил вопрос из БД.')


@message_exception_handler(
    log_error_text='Ошибка при выборе вопроса для обновления'
)
@info_router.callback_query(
    or_f(SectionState.general_questions, SectionState.problems_with_products),
    F.data == ADMIN_BASE_OPTIONS.get("update"),
)
async def update_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Запустить процесс выбора вопроса для обновления."""
    await question_update_manager.select_question(
        callback,
        state,
        next_state=UpdateQuestionStates.select,
        session=session,
    )
    logger.info(
        f'Пользователь {callback.from_user.id} выбрал вопрос для обновления.'
    )


@message_exception_handler(
    log_error_text='Ошибка при выборе данных для обновления вопроса'
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
    """Обработать выбор данных для обновления вопроса."""
    await question_update_manager.update_data_type(callback, session)
    logger.info(
        f'Пользователь {callback.from_user.id} выбрал данные для обновления вопроса.'
    )


@message_exception_handler(
    log_error_text='Ошибка при обновлении текста вопроса'
)
@info_router.callback_query(
    UpdateQuestionStates.select,
    F.data == ADMIN_QUESTION_OPTIONS.get("question"),
)
async def update_question_text(callback: CallbackQuery, state: FSMContext):
    """Обновить текст вопроса."""
    await question_update_manager.update_question(callback, state)
    logger.info(f'Пользователь {callback.from_user.id} обновил текст вопроса.')


@message_exception_handler(
    log_error_text='Ошибка при обновлении ответа на вопрос'
)
@info_router.callback_query(
    UpdateQuestionStates.select, F.data == ADMIN_QUESTION_OPTIONS.get("answer")
)
async def update_question_answer(callback: CallbackQuery, state: FSMContext):
    """Обновить ответ на вопрос."""
    await question_update_manager.update_answer(callback, state)
    logger.info(
        f'Пользователь {callback.from_user.id} обновил ответ на вопрос.'
    )


@message_exception_handler(
    log_error_text='Ошибка при обновлении данных вопроса в БД'
)
@info_router.message(
    or_f(UpdateQuestionStates.question, UpdateQuestionStates.answer), F.text
)
async def update_question_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Обновить вопрос в базе данных на основе нового содержимого."""
    await question_update_manager.update_question_in_db(
        message, state, session
    )
    logger.info(
        f'Пользователь {message.from_user.id} обновил данные вопроса в БД.'
    )
