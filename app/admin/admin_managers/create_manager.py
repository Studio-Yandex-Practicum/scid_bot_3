from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.handlers.validators import validate_button_name_len, validate_url
from admin.keyboards.keyboards import (
    get_inline_keyboard,
)
from admin.admin_settings import ADMIN_CONTENT_BUTTONS
from .base_manager import (
    BaseAdminManager,
)
from crud.base_crud import CRUDBase


class CreateState(StatesGroup):
    """Класс состояний для создания объекта в БД."""

    select = State()
    name = State()
    url = State()
    description = State()
    media = State()


class CreateManager(BaseAdminManager):
    """
    Менеджер для управления процессом создания объектов в базе данных.

    Этот класс обеспечивает обработку различных этапов ввода данных от пользователя
    для создания новых объектов. Он взаимодействует с базой данных через CRUD-операции
    и управляет состоянием пользователя в процессе ввода.

    Attributes:
        model_crud (CRUDBase): Объект для выполнения операций CRUD с моделью.
        back_option (str): Данные для возврата в меню.
        staes_group (StaesGroup): Набор машинных состояний

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

    def __init__(
        self,
        model_crud: CRUDBase,
        back_option: str,
        states_group: StatesGroup = CreateState(),
    ) -> None:
        super().__init__(model_crud, back_option, states_group)

    async def select_data_type(self, message: Message, state: FSMContext):
        """Выбрать тип данных для модели в БД."""
        await state.update_data(name=message.text)
        await message.answer(
            "Выбирите способ передачи информации:",
            reply_markup=await get_inline_keyboard(
                ADMIN_CONTENT_BUTTONS, previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.select)

    async def add_obj_name(
        self,
        callback: CallbackQuery,
        state: FSMContext,
    ):
        """
        Добавить название объекта и перейти в
        следующее машинное состояние.
        """
        await callback.message.delete()
        await callback.message.answer(
            "Введите название:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.name)

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
        if not validate_button_name_len(message.text):
            await message.answer(
                (
                    "Слишком длинное название для кнопки! Из-за ограничений "
                    "телеграма могут возникнуть проблемы :( "
                    "Попробуйте ввести название покороче."
                ),
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
            return
        await state.update_data(name=message.text)
        await message.answer(
            message_text,
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
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
            next_state=self.states_group.url,
        )

    async def add_obj_url_callback(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """
        Добавить ссылку к объекту и перейти в
        следующее машинное состояние.
        """
        await callback.message.answer(
            (
                "Ссылка обязательно должна начинаться с 'https://'\n\n "
                "Введите адрес ссылки:"
            ),
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.url)

    async def add_obj_description(self, message: Message, state: FSMContext):
        """
        Добавить текст к объекту и перейти в
        следующее машинное состояние.
        """
        message_text = "Введите описание:"
        await self.prompt_for_input(
            message,
            message_text,
            state,
            next_state=self.states_group.description,
        )

    async def add_obj_description_callback(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """
        Добавить текст к объекту и перейти в
        следующее машинное состояние.
        """
        await callback.message.answer(
            "Введите описание:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.description)

    async def add_obj_media(self, message: Message, state: FSMContext):
        """
        Добавить картинку к объекту и перейти в
        следующее машинное состояние.
        """
        message_text = (
            "Добавьте картинку и текст к ней. "
            "Длина текста не должна превышать 2200 символов:"
        )
        await self.prompt_for_input(
            message,
            message_text,
            state,
            next_state=self.states_group.media,
        )

    async def add_obj_media_callback(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """
        Добавить картинку к объекту и перейти в
        следующее машинное состояние.
        """
        await callback.message.answer(
            "Добавьте картинку и текст к ней:",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.media)

    async def add_obj_to_db(
        self, message: Message, state: FSMContext, session: AsyncSession
    ):
        """Добавить объект в БД и сбросить машинное состояние."""
        try:
            current_state = await state.get_state()
            if current_state == self.states_group.url.state:
                if not validate_url(message.text):
                    await message.answer(
                        ("Некорректный URL. Попробуйте добавить заново."),
                        reply_markup=await get_inline_keyboard(
                            previous_menu=self.back_option
                        ),
                    )
                    return
                await state.update_data(url=message.text)
            elif current_state == self.states_group.description.state:
                await state.update_data(description=message.text)
            elif current_state == self.states_group.media.state:
                await state.update_data(
                    media=message.photo[-1].file_id,
                    description=message.caption,
                )

            data = await state.get_data()
            await self.model_crud.create(data, session)

            await message.answer(
                "Данные добавлены!",
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
