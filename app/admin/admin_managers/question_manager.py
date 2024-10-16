from abc import ABC
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.keyboards.keyboards import (
    get_inline_confirmation,
    get_inline_keyboard,
)
from admin.admin_settings import ADMIN_QUESTION_BUTTONS, SUPPORT_OPTIONS
from crud.info_crud import info_crud


class CreateQuestionStates(StatesGroup):
    question = State()
    answer = State()


class UpdateQuestionStates(StatesGroup):
    select = State()
    question = State()
    answer = State()


class DeleteQuestionStates(StatesGroup):
    select = State()
    confirm = State()


class QuestionBaseManager(ABC):
    """
    Базовый класс для управления вопросами.
    Определяет основные методы для работы с вопросами и их типами.
    """

    async def set_question_type(self, state: FSMContext):
        state = await state.get_state()
        self.question_type = state.split(":")[-1]
        self.back_option = SUPPORT_OPTIONS.get(self.question_type)
        return self.back_option


class QuestionUpdateDeleteBase(QuestionBaseManager, ABC):
    """
    Базовый класс для управления обновлением и удалением вопросов.
    """

    async def get_question_list(self, session: AsyncSession):
        return [
            question.question
            for question in await info_crud.get_all_questions_by_type(
                self.question_type, session
            )
        ]

    async def select_question(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        next_state: State,
        session: AsyncSession,
    ):
        self.question_type = await self.set_question_type(state)
        questions = await self.get_question_list(session)
        await callback.message.edit_text(
            "Выберте вопрос:",
            reply_markup=await get_inline_keyboard(
                questions, previous_menu=self.back_option
            ),
        )
        await state.set_state(next_state)


class QuestionCreateManager(QuestionBaseManager):
    """
    Менеджер для создания вопросов.
    """

    async def add_question_text(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """
        Добавить текст вопроса и перейти в
        следующее машинное состояние.
        """
        await callback.message.delete()
        await state.update_data(
            question_type=await self.set_question_type(state)
        )
        await callback.message.answer(
            "Введите текст вопроса:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(CreateQuestionStates.question)

    async def add_answer_text(self, message: Message, state: FSMContext):
        """
        Добавить ответ и перейти в
        следующее машинное состояние.
        """
        await state.update_data(question=message.text)
        await message.answer(
            "Введите ответ на этот вопрос:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(CreateQuestionStates.answer)

    async def add_question_to_db(
        self,
        message: Message,
        state: FSMContext,
        session: AsyncSession,
    ):
        """Добавить вопрос в БД и сбросить машинное состояние."""
        try:
            await state.update_data(answer=message.text)
            data = await state.get_data()
            await info_crud.create(data, session=session)
            await message.answer(
                "Вопрос добавлен!",
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
            await state.clear()
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")


class QuestionUpdateManager(QuestionUpdateDeleteBase):
    """
    Менеджер для обновления вопросов.
    """

    async def update_data_type(
        self, callback: CallbackQuery, session: AsyncSession
    ):
        self.question = await info_crud.get_by_string(callback.data, session)
        await callback.message.edit_text(
            "Что отредактировать?",
            reply_markup=await get_inline_keyboard(
                ADMIN_QUESTION_BUTTONS, previous_menu=self.back_option
            ),
        )

    async def update_question(
        self, callback: CallbackQuery, state: FSMContext
    ):
        await callback.message.edit_text(
            f"Текущий текст вопроса: \n\n {self.question.question}\n\n Введите новый текст:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(UpdateQuestionStates.question)

    async def update_answer(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            f"Текущий текст ответа: {self.question.answer}\n\n Введите новый текст:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.question_type
            ),
        )
        await state.set_state(UpdateQuestionStates.answer)

    async def update_question_in_db(
        self, message: Message, state: FSMContext, session: AsyncSession
    ):
        current_state = await state.get_state()
        if current_state == UpdateQuestionStates.question.state:
            await state.update_data(question=message.text)
        elif current_state == UpdateQuestionStates.answer.state:
            await state.update_data(answer=message.text)
        data = await state.get_data()
        await info_crud.update(self.question, data, session)
        await message.answer(
            "Данные обновлены!",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.clear()


class QuestionDeleteManager(QuestionUpdateDeleteBase):
    """
    Менеджер для удаления вопросов.
    """

    async def confirm_delete(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        self.question = await info_crud.get_by_string(callback.data, session)
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить этот вопрос'?\n\n {self.question.question}",
            reply_markup=await get_inline_confirmation(
                cancel_option=self.back_option
            ),
        ),
        await state.set_state(DeleteQuestionStates.confirm)

    async def delete_question(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        """Удалить вопрос из БД."""
        try:
            await info_crud.remove(self.question, session)
            await callback.message.edit_text(
                "Вопрос удален!",
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
            await state.clear()
        except Exception as e:
            await callback.message.answer(f"Произошла ошибка: {e}")
