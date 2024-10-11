from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.admin_orm.base_manager import (
    BaseAdminManager,
    CreateUpdateState,
)
from app.admin.keyboards.keyboards import InlineKeyboardManager
from app.const import ADMIN_UPDATE_BUTTONS


class UpdateState(CreateUpdateState):
    """Класс состояний для редактирования данных в БД."""

    pass


class UpdateManager(BaseAdminManager):
    """
    Менеджер для редактирования объектов в базе данных.

    Этот класс предоставляет функциональность для получения списка объектов,
    выбора объекта для редактирования, выбора данных для обновления и
    внесения изменений в объекты. Он управляет состоянием пользователя
    в процессе редактирования и взаимодействует с базой данных
    через CRUD-операции.

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
            reply_markup=self.keyboard.add_extra_buttons(obj_list_by_name),
        )
        await state.set_state(UpdateState.select)

    async def select_data_to_update(
        self,
        callback: CallbackQuery,
        session: AsyncSession,
    ):
        """Выбрать поле редактирования для модели в БД."""
        self.obj_to_update = await self.model_crud.get_by_string(
            callback.data, session
        )
        keyboard = InlineKeyboardManager(ADMIN_UPDATE_BUTTONS)
        await keyboard.add_previous_menu_button(self.keyboard.previous_menu)
        await callback.message.edit_text(
            "Выбирите данные для обновления:",
            reply_markup=keyboard.create_keyboard(),
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
            reply_markup=InlineKeyboardManager.get_back_button(
                self.keyboard.previous_menu
            ),
        )
        await state.set_state(UpdateState.name)

    async def change_obj_content(
        self, callback: CallbackQuery, state: FSMContext
    ):
        """Внести изменение в содержание объекта."""
        if not self.obj_to_update.media:
            if self.obj_to_update.url:
                message_text = (
                    f"Текущий адрес ссылки: \n\n {self.obj_to_update.url} \n\n"
                    "Введите новый:"
                )
                await state.set_state(UpdateState.url)
            elif self.obj_to_update.text and not self.obj_to_update.media:
                message_text = (
                    f"Текущий текст: \n\n {self.obj_to_update.text} \n\n"
                    "Введите новый:"
                )
                await state.set_state(UpdateState.text)
            await callback.message.edit_text(
                message_text,
                reply_markup=InlineKeyboardManager.get_back_button(
                    self.keyboard.previous_menu
                ),
            )
        else:
            await callback.message.answer("Текущая картинка:")
            await callback.message.answer_photo(
                photo=self.obj_to_update.media,
                caption=self.obj_to_update.text,
            )
            await callback.message.answer(
                "Добавьте новую картинку и описание",
                reply_markup=InlineKeyboardManager.get_back_button(
                    self.keyboard.previous_menu,
                ),
            )
            await state.set_state(UpdateState.media)

    async def update_obj_in_db(
        self, message: Message, state: FSMContext, session: AsyncSession
    ):
        """Внести изменения объекта в БД."""
        try:
            current_state = await state.get_state()
            if current_state == UpdateState.url.state:
                await state.update_data(url=message.text)
            elif current_state == UpdateState.text.state:
                await state.update_data(text=message.text)
            elif current_state == UpdateState.media.state:
                await state.update_data(
                    media=message.photo[-1].file_id,
                    text=message.caption,
                )

            data = await state.get_data()
            await self.model_crud.update(self.obj_to_update, data, session)

            await message.answer(
                "Данные обновлены!",
                reply_markup=InlineKeyboardManager.get_back_button(
                    self.keyboard.previous_menu
                ),
            )
            await state.clear()
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
