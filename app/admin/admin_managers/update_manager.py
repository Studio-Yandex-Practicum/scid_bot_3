from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from crud.base_crud import CRUDBase
from crud.portfolio_projects_crud import portfolio_crud

from .base_manager import (
    BaseAdminManager,
)
from admin.keyboards.keyboards import (
    get_inline_keyboard,
)
from admin.admin_settings import ADMIN_UPDATE_BUTTONS


class UpdateState(StatesGroup):
    """Класс состояний для редактирования данных в БД."""

    select = State()
    name = State()
    url = State()
    description = State()
    media = State()
    portolio = State()


class UpdateManager(BaseAdminManager):
    """
    Менеджер для редактирования объектов в базе данных.

    Этот класс предоставляет функциональность для получения списка объектов,
    выбора объекта для редактирования, выбора данных для обновления и
    внесения изменений в объекты. Он управляет состоянием пользователя
    в процессе редактирования и взаимодействует с базой данных
    через CRUD-операции.

    Attributes:
        model_crud (CRUDBase): Объект для выполнения операций CRUD с моделью.
        back_option (str): Данные для возврата в меню.

    Methods:
        get_all_model_names(session: AsyncSession) -> list[str]:
            Получает список названий объектов из таблицы БД.

        select_obj_to_update(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
            Запрашивает у пользователя, какой объект он хочет отредактировать, и отображает список объектов.

        select_data_to_update(callback: CallbackQuery, session: AsyncSession) -> None:
            Позволяет выбрать поле для редактирования объекта в БД.

        change_obj_name(callback: CallbackQuery, state: FSMContext) -> None:
            Запрашивает новое название для объекта и обновляет состояние.

        change_obj_content(callback: CallbackQuery, state: FSMContext) -> None:
            Позволяет пользователю изменить содержание объекта, включая текст, URL и медиафайлы.

        update_obj_in_db(message: Message, state: FSMContext, session: AsyncSession) -> None:
            Вносит изменения в объект в БД и сбрасывает состояние.
    """

    def __init__(
        self,
        model_crud: CRUDBase,
        back_option: str,
        states_group: StatesGroup = UpdateState(),
    ) -> None:
        super().__init__(model_crud, back_option, states_group)

    async def get_all_model_names(self, session: AsyncSession) -> list[str]:
        """Получить список названий объектов из таблицы БД."""
        models = await self.model_crud.get_multi(session)
        return [model.name for model in models]

    async def select_obj_to_update(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
    ) -> None:
        obj_list_by_name = await self.get_all_model_names(session)
        await callback.message.edit_text(
            "Какой объект отредактировать?",
            reply_markup=await get_inline_keyboard(
                obj_list_by_name, previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.select)

    async def select_data_to_update(
        self,
        callback: CallbackQuery,
        session: AsyncSession,
    ):
        """Выбрать поле редактирования для модели в БД."""
        self.obj_to_update = await self.model_crud.get_by_string(
            callback.data, session
        )
        await callback.message.edit_text(
            "Выбирите данные для обновления:",
            reply_markup=await get_inline_keyboard(
                ADMIN_UPDATE_BUTTONS, previous_menu=self.back_option
            ),
        )

    async def change_obj_name(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """Внести изменение в название объекта."""
        message_text = (
            f"Текущее название: \n\n {self.obj_to_update.name} \n\n"
            "Введите новое:"
        )
        await callback.message.edit_text(
            message_text,
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
        await state.set_state(self.states_group.name)

    async def change_obj_content(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """Внести изменение в содержание объекта."""
        obj_fields = self.obj_to_update.__dict__.keys()
        if "media" not in obj_fields or not self.obj_to_update.media:
            if "url" in obj_fields and self.obj_to_update.url:
                message_text = (
                    f"Текущий адрес ссылки: \n\n {self.obj_to_update.url} \n\n"
                    "Введите новый:"
                )
                await state.set_state(self.states_group.url)
            elif (
                "description" in obj_fields and self.obj_to_update.description
            ):
                message_text = (
                    f"Текущий текст: \n\n {self.obj_to_update.description} \n\n"
                    "Введите новый:"
                )
                await state.set_state(self.states_group.description)
            await callback.message.edit_text(
                message_text,
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
        else:
            await callback.message.answer("Текущая картинка:")
            await callback.message.answer_photo(
                photo=self.obj_to_update.media,
                caption=self.obj_to_update.description,
            )
            await callback.message.answer(
                "Добавьте новую картинку и описание",
                reply_markup=await get_inline_keyboard(
                    previous_menu=self.back_option
                ),
            )
            await state.set_state(self.states_group.media)

    async def update_obj_in_db(
        self, message: Message, state: FSMContext, session: AsyncSession
    ):
        """Внести изменения объекта в БД."""

        current_state = await state.get_state()
        if current_state == self.states_group.name.state:
            await state.update_data(name=message.text)
        elif current_state == self.states_group.url.state:
            await state.update_data(url=message.text)
        elif current_state == self.states_group.description.state:
            await state.update_data(description=message.text)
        elif current_state == self.states_group.media.state:
            await state.update_data(
                media=message.photo[-1].file_id,
                description=message.caption,
            )

        data = await state.get_data()
        await self.model_crud.update(self.obj_to_update, data, session)

        await message.answer(
            "Данные обновлены!",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )


class UpdatePortfolio:
    """
    Менеджер для редактирования ссылки основного портфолио в базе данных.

    Attributes:
        back_option (str): Данные для возврата в меню.

    Methods:
        update_main_portfolio_url(
            message: Message,
            state: FSMContext,
            session: AsyncSession) -> None:
            Позволяет пользователю изменить URL основного портфолио.
        update_obj_in_db(
            message: Message,
            state: FSMContext,
            session: AsyncSession) -> None:
            Вносит изменения в объект в БД и сбрасывает состояние.
    """

    def __init__(self, back_option: str) -> None:
        self.back_option = back_option

    async def update_main_portfolio_url(
        self, callback: CallbackQuery, state: FSMContext, session: AsyncSession
    ):
        """Изменить URL основного портфолио."""
        self.obj_to_update = await portfolio_crud.get_portfolio(session)
        message_text = (
            f"Текущий адрес ссылки: \n\n {self.obj_to_update.url} \n\n"
            "Введите новый:"
        )
        await state.set_state(self.states_group.portolio)
        await callback.message.edit_text(
            message_text,
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )

    async def update_obj_in_db(
        self, message: Message, state: FSMContext, session: AsyncSession
    ):
        """Внести изменения объекта в БД."""

        await state.update_data(url=message.text)
        data = await state.get_data()
        await portfolio_crud.update(self.obj_to_update, data, session)

        await message.answer(
            "Данные обновлены!",
            reply_markup=await get_inline_keyboard(
                previous_menu=self.back_option
            ),
        )
