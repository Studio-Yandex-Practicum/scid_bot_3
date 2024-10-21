import logging

from aiogram import F, Router
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from admin.handlers.admin_handlers.admin import SectionState
from bot.exceptions import message_exception_handler
from crud import portfolio_crud
from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.admin_managers import (
    DeleteManager,
    CreateManager,
    UpdateManager,
    UpdatePortfolio,
)
from admin.admin_settings import (
    ADMIN_UPDATE_OPTIONS,
    MAIN_MENU_OPTIONS,
    ADMIN_PORTFOLIO_OPTIONS,
    PORTFOLIO_MENU_OPTIONS,
    ADMIN_BASE_OPTIONS,
)

logger = logging.getLogger(__name__)

portfolio_router = Router()
portfolio_router.message.filter(
    ChatTypeFilter(["private"]), IsManagerOrAdmin()
)
portfolio_router.callback_query(IsManagerOrAdmin())

PREVIOUS_MENU = PORTFOLIO_MENU_OPTIONS.get("other_projects")


class PortfolioCreateState(StatesGroup):
    name = State()
    url = State()


class PortfolioDeleteState(StatesGroup):
    select = State()
    confirm = State()


class PortfolioUpdateState(StatesGroup):
    select = State()
    name = State()
    url = State()
    portfolio = State()


portfolio_create_manager = CreateManager(
    portfolio_crud, PREVIOUS_MENU, PortfolioCreateState()
)
portfolio_delete_manager = DeleteManager(
    portfolio_crud, PREVIOUS_MENU, PortfolioDeleteState()
)
portfolio_update_manager = UpdateManager(
    portfolio_crud, PREVIOUS_MENU, PortfolioUpdateState
)
main_portfolio_url_update_manager = UpdatePortfolio(
    MAIN_MENU_OPTIONS.get("portfolio"), PortfolioUpdateState()
)


@message_exception_handler(
    log_error_text="Ошибка при добавлении имени проекта портфолио"
)
@portfolio_router.callback_query(
    SectionState.other_projects, F.data == ADMIN_BASE_OPTIONS.get("create")
)
async def add_portfolio_project_name(
    callback: CallbackQuery, state: FSMContext
):
    """Запустить процесс создания нового портфолио."""
    await portfolio_create_manager.add_obj_name(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} запустил процесс создания нового портфолио."
    )


@message_exception_handler(
    log_error_text="Ошибка при сохранении имени нового объекта портфолио"
)
@portfolio_router.message(PortfolioCreateState.name, F.text)
async def add_portfolio_project_url(message: Message, state: FSMContext):
    """Сохранить имя нового объекта в состояние."""
    await portfolio_create_manager.add_obj_url(message, state)
    logger.info(
        f"Пользователь {message.from_user.id} сохранил имя нового объекта портфолио."
    )


@message_exception_handler(
    log_error_text="Ошибка при сохранении URL нового объекта в БД"
)
@portfolio_router.message(PortfolioCreateState.url, F.text)
async def create_portfolio_project(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Сохранить URL нового объекта в базу данных."""
    await portfolio_create_manager.add_obj_to_db(message, state, session)
    logger.info(
        f"Пользователь {message.from_user.id} создал новый проект портфолио в БД."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе портфолио для удаления"
)
@portfolio_router.callback_query(
    SectionState.other_projects, F.data == ADMIN_BASE_OPTIONS.get("delete")
)
async def portfolio_project_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Запустить процесс выбора объекта для удаления."""
    await portfolio_delete_manager.select_obj_to_delete(
        callback, state, session
    )
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал проект для удаления."
    )


@message_exception_handler(
    log_error_text="Ошибка при подтверждении удаления проекта"
)
@portfolio_router.callback_query(
    PortfolioDeleteState.select, F.data != PREVIOUS_MENU
)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Подтвердить удаление выбранного объекта."""
    await portfolio_delete_manager.confirm_delete(callback, state, session)
    logger.info(
        f"Пользователь {callback.from_user.id} подтвердил удаление проекта."
    )


@message_exception_handler(log_error_text="Ошибка при удалении проекта из БД")
@portfolio_router.callback_query(
    PortfolioDeleteState.confirm, F.data != PREVIOUS_MENU
)
async def delete_portfolio_project(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Удалить выбранный объект из базы данных."""
    await portfolio_delete_manager.delete_obj(callback, state, session)
    logger.info(f"Пользователь {callback.from_user.id} удалил проект из БД.")


@message_exception_handler(
    log_error_text="Ошибка при выборе проекта для обновления"
)
@portfolio_router.callback_query(
    SectionState.other_projects, F.data == ADMIN_BASE_OPTIONS.get("update")
)
async def portfolio_project_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Запустить процесс выбора объекта для обновления."""
    await portfolio_update_manager.select_obj_to_update(
        callback, state, session
    )
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал проект для обновления."
    )


@message_exception_handler(
    log_error_text="Ошибка при выборе данных для обновления"
)
@portfolio_router.callback_query(
    PortfolioUpdateState.select,
    and_f(
        F.data != ADMIN_UPDATE_OPTIONS.get("name"),
        F.data != ADMIN_UPDATE_OPTIONS.get("content"),
        F.data != PREVIOUS_MENU,
    ),
)
async def update_portfolio_project_choice(
    callback: CallbackQuery, session: AsyncSession
):
    """Обработать выбор данных для обновления."""
    await portfolio_update_manager.select_data_to_update(callback, session)
    logger.info(
        f"Пользователь {callback.from_user.id} выбрал данные для обновления."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении имени объекта"
)
@portfolio_router.callback_query(
    PortfolioUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("name")
)
async def portfolio_name_update(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Обновить имя объекта."""
    await portfolio_update_manager.change_obj_name(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} обновил имя объекта портфолио."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении содержимого объекта"
)
@portfolio_router.callback_query(
    PortfolioUpdateState.select, F.data == ADMIN_UPDATE_OPTIONS.get("content")
)
async def about_url_update(callback: CallbackQuery, state: FSMContext):
    """Обновить содержимое объекта."""
    await portfolio_update_manager.change_obj_content(callback, state)
    logger.info(
        f"Пользователь {callback.from_user.id} обновил содержимое объекта портфолио."
    )


@message_exception_handler(log_error_text="Ошибка при обновлении объекта в БД")
@portfolio_router.message(
    or_f(PortfolioUpdateState.name, PortfolioUpdateState.url), F.text
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Обновить объект в базе данных на основе нового содержимого."""
    await portfolio_update_manager.update_obj_in_db(message, state, session)
    logger.info(f"Пользователь {message.from_user.id} обновил объект в БД.")


@message_exception_handler(
    log_error_text="Ошибка при обновлении адреса ссылки основного портфолио"
)
@portfolio_router.callback_query(
    SectionState.portfolio,
    F.data == ADMIN_PORTFOLIO_OPTIONS.get("change_url"),
)
async def change_portfolio_url(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Обновить адрес ссылки основного портфолио."""
    await main_portfolio_url_update_manager.update_main_portfolio_url(
        callback, state, session
    )
    logger.info(
        f"Пользователь {callback.from_user.id} обновил адрес ссылки основного портфолио."
    )


@message_exception_handler(
    log_error_text="Ошибка при обновлении адреса ссылки основного портфолио в БД"
)
@portfolio_router.message(PortfolioUpdateState.portfolio, F.text)
async def update_portfolio_button(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Обновить адрес ссылки основного портфолио в базе данных."""
    await main_portfolio_url_update_manager.update_obj_in_db(
        message, state, session
    )
    logger.info(
        f"Пользователь {message.from_user.id} обновил адрес ссылки основного портфолио в БД."
    )
