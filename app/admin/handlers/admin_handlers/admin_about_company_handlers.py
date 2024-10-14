import logging

from aiogram import F, Router
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession


from .admin import SectionState
from bot.exceptions import message_exception_handler
from crud.about_crud import company_info_crud
from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.admin_managers import (
    DeleteManager,
    DeleteState,
    CreateState,
    CreateManager,
    UpdateManager,
    UpdateState,
)

from admin.admin_settings import (
    ADMIN_BASE_OPTIONS,
    ADMIN_UPDATE_OPTIONS,
    MAIN_MENU_OPTIONS,
)

logger = logging.getLogger(__name__)

PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("company_bio")

about_router = Router()
about_router.message.filter(ChatTypeFilter(["private"]), IsManagerOrAdmin())

about_create_manager = CreateManager(company_info_crud, PREVIOUS_MENU)
about_delete_manager = DeleteManager(company_info_crud, PREVIOUS_MENU)
about_update_manager = UpdateManager(company_info_crud, PREVIOUS_MENU)


@message_exception_handler(
    log_error_text="Ошибка при создании новой информации о компании"
)
@about_router.callback_query(
    SectionState.about, F.data == ADMIN_BASE_OPTIONS.get("create")
)
async def create_about_info(callback: CallbackQuery, state: FSMContext):
    """Запустить процесс создания новой информации о компании."""
    await about_create_manager.add_obj_name(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} начал создание новой информации о компании."
    )


@message_exception_handler(
    log_error_text="Ошибка при сохранении имени нового объекта"
)
@about_router.message(CreateState.name, F.text)
async def add_info_name(message: Message, state: FSMContext):
    """Сохранить имя нового объекта в состояние."""
    await about_create_manager.add_obj_url(message, state)
    logger.info(
        f"Пользователь {message.from_user.id} сохранил имя нового объекта."
    )


@message_exception_handler(
    log_error_text="Ошибка при сохранении URL нового объекта"
)
@about_router.message(CreateState.url, F.text)
async def add_about_data(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Сохранить URL нового объекта в базу данных."""
    await about_create_manager.add_obj_to_db(message, state, session)
    logger.info(
        f"Пользователь {message.from_user.id} сохранил URL нового объекта."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе объекта для удаления"
)
@about_router.callback_query(
    SectionState.about, F.data == ADMIN_BASE_OPTIONS.get("delete")
)
async def about_info_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Запустить процесс выбора объекта для удаления."""
    await about_delete_manager.select_obj_to_delete(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал объект для удаления."
    )


@message_exception_handler(
    log_error_text="Ошибка при подтверждении удаления информации"
)
@about_router.callback_query(DeleteState.select, F.data != PREVIOUS_MENU)
async def confirm_delete_info(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтвердить удаление выбранного объекта."""
    await about_delete_manager.confirm_delete(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} подтвердил удаление информации."
    )


@message_exception_handler(
    log_error_text="Ошибка при удалении информации из базы данных"
)
@about_router.callback_query(DeleteState.confirm, F.data != PREVIOUS_MENU)
async def delete_about_info(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить выбранный объект из базы данных."""
    await about_delete_manager.delete_obj(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} удалил информацию из базы данных."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе объекта для обновления"
)
@about_router.callback_query(
    SectionState.about, F.data == ADMIN_BASE_OPTIONS.get("update")
)
async def about_info_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Запустить процесс выбора объекта для обновления."""
    await about_update_manager.select_obj_to_update(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал объект для обновления."
    )


@message_exception_handler(
    log_error_text="Ошибка при обработке выбора данных для обновления"
)
@about_router.callback_query(
    UpdateState.select,
    and_f(
        F.data != ADMIN_UPDATE_OPTIONS.get("name"),
        F.data != ADMIN_UPDATE_OPTIONS.get("content"),
        F.data != PREVIOUS_MENU,
    ),
)
async def update_info_choice(callback: CallbackQuery, session: AsyncSession):
    """Обработать выбор данных для обновления."""
    await about_update_manager.select_data_to_update(callback, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал данные для обновления."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении имени объекта"
)
@about_router.callback_query(
    UpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("name")
)
async def about_name_update(callback: CallbackQuery, state: FSMContext):
    """Обновить имя объекта."""
    await about_update_manager.change_obj_name(callback, state)
    logger.info(f"Пользователь {callback.from_user.id} обновил имя объекта.")


@message_exception_handler(
    log_error_text="Ошибка при обновлении содержимого объекта"
)
@about_router.callback_query(
    UpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("content")
)
async def about_url_update(callback: CallbackQuery, state: FSMContext):
    """Обновить содержимое объекта."""
    await about_update_manager.change_obj_content(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} обновил содержимое объекта."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении информации в базе данных"
)
@about_router.message(or_f(UpdateState.name, UpdateState.url), F.text)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Обновить объект в базе данных на основе нового содержимого."""
    await about_update_manager.update_obj_in_db(message, state, session)
    logger.info(
        f"Пользователь {message.from_user.id} обновил информацию о компании в базе данных."
    )
