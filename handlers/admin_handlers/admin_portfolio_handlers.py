from aiogram import F, Router
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from .admin import SectionState
from CRUD.about_crud import company_info_crud
from CRUD.portfolio_projects_crud import portfolio_сrud
from filters.filters import ChatTypeFilter, IsAdmin
from keyboards.keyboards import (
    get_inline_confirmation_keyboard,
    get_inline_keyboard,
)
from settings import (
    MAIN_MENU_OPTIONS,
    ADMIN_PORTFOLIO_OPTIONS,
    PORTFOLIO_MENU_OPTIONS,
)

portfolio_router = Router()
portfolio_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class UpdatePortfolio(StatesGroup):
    url = State()


class AddProject(StatesGroup):
    project_name = State()
    url = State()


class UpdateProject(StatesGroup):
    select = State()
    project_name = State()
    url = State()
    confirm = State()


class DeleteProject(AddProject):
    confirm = State()


PREVIOUS_MENU = PORTFOLIO_MENU_OPTIONS.get("other_projects")


async def get_portfolio_project_list(session: AsyncSession):
    """Получить список названий проектов для портфолио."""
    projects = [
        project.project_name
        for project in await portfolio_сrud.get_multi(session)
    ]
    return projects


@portfolio_router.callback_query(
    SectionState.other_projects, F.data == "Добавить"
)
async def add_portfolio_project_name(
    callback: CallbackQuery, state: FSMContext
):
    await callback.message.answer("Введите название проекта:")
    await state.set_state(AddProject.project_name)


@portfolio_router.message(AddProject.project_name, F.text)
async def add_portfolio_project_url(message: Message, state: FSMContext):
    await state.update_data(project_name=message.text)
    await message.answer("Добавьте ссылку:")
    await state.set_state(AddProject.url)


@portfolio_router.message(AddProject.url, F.text)
async def create_portfolio_project(
    message: Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(url=message.text)
    data = await state.get_data()
    await portfolio_сrud.create(data, session)
    await message.answer(
        "Проект добавлен!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
    await state.clear()


@portfolio_router.callback_query(
    SectionState.other_projects, F.data == "Удалить"
)
async def portfolio_project_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.answer(
        "Какой проект Вы хотите удалить?",
        reply_markup=await get_inline_keyboard(
            options=await get_portfolio_project_list(session),
            previous_menu=PREVIOUS_MENU,
        ),
    )
    await state.set_state(DeleteProject.project_name)


@portfolio_router.callback_query(DeleteProject.project_name, F.data)
async def confirm_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    portfolio_project = await portfolio_сrud.get_by_project_name(
        callback.data, session
    )
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить этот проект?\n\n {portfolio_project.project_name}",
        reply_markup=await get_inline_confirmation_keyboard(
            option=portfolio_project.project_name, cancel_option=PREVIOUS_MENU
        ),
    )
    await state.set_state(DeleteProject.confirm)


@portfolio_router.callback_query(
    DeleteProject.confirm, F.data != PREVIOUS_MENU
)
async def delete_protfolio_project(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    portfolio_project = await portfolio_сrud.get_by_project_name(
        callback.data, session
    )
    await portfolio_сrud.remove(portfolio_project, session)
    await callback.message.edit_text(
        "Проект удален!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
    await state.clear()


@portfolio_router.callback_query(
    SectionState.other_projects, F.data == "Изменить"
)
async def portfolio_project_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.edit_text(
        "Какую информацию вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            options=await get_portfolio_project_list(session),
            previous_menu=PREVIOUS_MENU,
        ),
    )
    await state.set_state(UpdateProject.select)


@portfolio_router.callback_query(
    UpdateProject.select,
    and_f(F.data != "Название проекта", F.data != "Адрес ссылки", F.data != PREVIOUS_MENU),
)
async def update_portfolio_project_choise(
    callback: CallbackQuery, state: FSMContext
):
    await state.update_data(select=callback.data)
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            ["Название проекта", "Адрес ссылки"], previous_menu=PREVIOUS_MENU
        ),
    )


@portfolio_router.callback_query(
    UpdateProject.select, F.data == "Название проекта"
)
async def about_name_update(
    callback: CallbackQuery, state: FSMContext,
):
    about_name = await state.get_data()
    about_name_text = about_name.get("select")
    await callback.message.answer(
        f"Сейчас у проекта такое название:\n\n {about_name_text}\n\n Введите новое название"
    )
    await state.set_state(UpdateProject.project_name)


@portfolio_router.callback_query(
    UpdateProject.select, F.data == "Адрес ссылки"
)
async def about_url_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_name_data = await state.get_data()
    about_name_text = about_name_data.get("select")
    about_info = await portfolio_сrud.get_by_project_name(
        about_name_text, session
    )
    await callback.message.answer(
        f"Сейчас у ссылки такой адрес:\n\n {about_info.url}\n\n Введите новое название"
    )
    await state.set_state(UpdateProject.url)


@portfolio_router.message(
    or_f(UpdateProject.project_name, UpdateProject.url), F.text
)
async def update_about_info(
    message: Message, state: FSMContext, session: AsyncSession
):
    current_state = await state.get_state()
    old_data = await state.get_data()
    old_portfolio_data = await portfolio_сrud.get_by_project_name(
        old_data.get("select"), session
    )
    if current_state == UpdateProject.project_name:
        await state.update_data(project_name=message.text)
    elif current_state == UpdateProject.url:
        await state.update_data(url=message.text)
    update_data = await state.get_data()
    await portfolio_сrud.update(old_portfolio_data, update_data, session)
    await message.answer(
        "Информация обновлена!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
    await state.clear()


@portfolio_router.callback_query(
    SectionState.portfolio,
    F.data == ADMIN_PORTFOLIO_OPTIONS.get("change_url"),
)
async def change_portfolio_url(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый адрес ссылки на портфолио")
    await state.set_state(UpdatePortfolio.url)


@portfolio_router.message(UpdatePortfolio.url, F.text)
async def update_portfolio_button(
    message: Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(url=message.text)
    updated_data = await state.get_data()
    portfolio = await company_info_crud.get_portfolio(session)
    await company_info_crud.update(portfolio, updated_data, session)
    await message.answer(
        "Изменения внесены!",
        reply_markup=await get_inline_keyboard(
            previous_menu=MAIN_MENU_OPTIONS.get("portfolio")
        ),
    )
    await state.clear()
