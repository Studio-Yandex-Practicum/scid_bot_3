from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.admin_orm.manager_base import (
    BaseAdminManager,
    CreateUpdateState,
)
from app.admin.keyboards.keyboards import InlineKeyboardManager
from app.const import ADMIN_CONTENT_BUTTONS


class CreateState(CreateUpdateState):
    """Класс состояний для создания объекта в БД."""

    pass


class CreateManager(BaseAdminManager):
    """
    Менеджер для управления процессом создания объектов в базе данных.

    Этот класс обеспечивает обработку различных этапов ввода данных от пользователя
    для создания новых объектов. Он взаимодействует с базой данных через CRUD-операции
    и управляет состоянием пользователя в процессе ввода.

    Attributes:
        model_crud (CRUDBase): Объект для выполнения операций CRUD с моделью.
        keyboard (InlineKeyboardManager): Менеджер для создания интерактивных клавиатур.

    Methods:
        select_data_type(callback: CallbackQuery, state: FSMContext):
            Запрашивает у пользователя тип данных для создания.

        prompt_for_input(message: Message, prompt: str, next_state: State):
            Отправляет сообщение с просьбой ввести данные и устанавливает следующее состояние.

        add_obj_name(callback: CallbackQuery, state: FSMContext):
            Запрашивает название объекта у пользователя.

        add_obj_url(message: Message, state: FSMContext):
            Запрашивает URL объекта у пользователя.

        add_obj_text(message: Message, state: FSMContext):
            Запрашивает текст объекта у пользователя.

        add_obj_media(message: Message, state: FSMContext):
            Запрашивает медиафайл и текст к нему у пользователя.

        add_obj_to_db(message: Message, state: FSMContext, session: AsyncSession):
            Добавляет объект в базу данных и сбрасывает машинное состояние.
    """

    async def select_data_type(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """Выбрать тип данных для модели в БД."""
        await callback.message.edit_text(
            "Выбирите способ передачи информации:",
            reply_markup=await self.keyboard.add_extra_buttons(
                ADMIN_CONTENT_BUTTONS
            ),
        )
        await state.set_state(CreateState.select)

    async def add_obj_name(
        self,
        callback: CallbackQuery,
        state: FSMContext,
    ):
        """
        Добавить название объекта и перейти в
        следующее машинное состояние.
        """
        await callback.message.answer(
            "Введите название:", reply_markup=self.keyboard
        )
        await state.set_state(CreateState.name)

    async def prompt_for_input(
        self,
        message: Message,
        message_text: str,
        state: FSMContext,
        next_state: State,
    ):
        """
        Добавить название объекта в state_data и перейти
        к заполнению следующего поля.
        """
        await state.update_data(name=message.text)
        await message.answer(
            message_text,
            reply_markup=self.keyboard,
        )
        await state.set_state(next_state)

    async def add_obj_url(self, message: Message, state: FSMContext):
        """
        Добавить ссылку к объекту и перейти в
        следующее машинное состояние.
        """
        message_text = (
            "Ссылка обязательно должна начинаться с 'https://'\n\n "
            "Введите адрес ссылки:"
        )
        await self.prompt_for_input(
            message,
            message_text,
            state,
            next_state=CreateState.url,
        )

    async def add_obj_text(self, message: Message, state: FSMContext):
        """
        Добавить текст к объекту и перейти в
        следующее машинное состояние.
        """
        message_text = "Введите текст:"
        await self.prompt_for_input(
            message,
            message_text,
            state,
            next_state=CreateState.text,
        )

    async def add_obj_media(self, message: Message, state: FSMContext):
        """
        Добавить картинку к объекту и перейти в
        следующее машинное состояние.
        """
        message_text = "Добавьте картинку и текст к ней:"
        await self.prompt_for_input(
            message,
            message_text,
            state,
            next_state=CreateState.media,
        )

    async def add_obj_to_db(
        self, message: Message, state: FSMContext, session: AsyncSession
    ):
        """Добавить объект в БД и сбросить машинное состояние."""
        try:
            current_state = await state.get_state()
            if current_state == CreateState.url.state:
                await state.update_data(url=message.text)
            elif current_state == CreateState.text.state:
                await state.update_data(text=message.text)
            elif current_state == CreateState.media.state:
                await state.update_data(
                    media=message.photo[-1].file_id,
                    text=message.caption,
                )

            data = await state.get_data()
            await self.model_crud.create(data, session)

            await message.answer(
                "Данные добавлены!",
                reply_markup=await InlineKeyboardManager.get_back_button(
                    self.keyboard.previous_menu
                ),
            )
            await state.clear()
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
