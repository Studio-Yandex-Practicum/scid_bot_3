from aiogram import F, Router
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from .admin import SectionState
from crud.about_crud import company_info_crud
from admin.filters.filters import ChatTypeFilter, IsAdmin
from admin.keyboards.keyboards import (
    get_inline_confirmation_keyboard,
    get_inline_keyboard,
)

# from settings import MAIN_MENU_OPTIONS

MAIN_MENU_OPTIONS = {
    "company_bio": "Информация о компании",
    "products": "Продукты и услуги",
    "support": "Техническая поддержка",
    "portfolio": "Портфолио",
    "request_callback": "Связаться с менеджером",
}

about_router = Router()
about_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class AddAboutInfo(StatesGroup):
    name = State()
    url = State()


class UpdateAboutInfo(StatesGroup):
    select = State()
    name = State()
    url = State()
    confirm = State()


class DeleteAboutInfo(AddAboutInfo):
    confirm = State()


PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("company_bio")


@about_router.callback_query(SectionState.about, F.data == "Добавить")
async def create_about_info(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название для ссылки:")
    await state.set_state(AddAboutInfo.name)


@about_router.message(AddAboutInfo.name, F.text)
async def add_info_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Добавьте ссылку:")
    await state.set_state(AddAboutInfo.url)


@about_router.message(AddAboutInfo.url, F.text)
async def add_about_data(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(url=message.text)
    data = await state.get_data()
    await company_info_crud.create(data, session)
    await message.answer(
        "Информация добавлена!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
    await state.clear()


@about_router.callback_query(SectionState.about, F.data == "Удалить")
async def about_info_to_delete(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_data = await company_info_crud.get_multi(session)
    info_list = [info.name for info in about_data]
    await callback.message.answer(
        "Какую информацию вы хотите удалить?",
        reply_markup=await get_inline_keyboard(info_list, previous_menu=PREVIOUS_MENU),
    )
    await state.set_state(DeleteAboutInfo.name)


@about_router.callback_query(DeleteAboutInfo.name, F.data)
async def confirm_delete_info(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_data = await company_info_crud.get_by_about_name(callback.data, session)
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить эту информацию?\n\n {about_data.name}",
        reply_markup=await get_inline_confirmation_keyboard(
            option=about_data.name, cancel_option=PREVIOUS_MENU
        ),
    )
    await state.set_state(DeleteAboutInfo.confirm)


@about_router.callback_query(DeleteAboutInfo.confirm, F.data != PREVIOUS_MENU)
async def delete_about_info(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_data = await company_info_crud.get_by_about_name(callback.data, session)
    await company_info_crud.remove(about_data, session)
    await callback.message.edit_text(
        "Информация удалена!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
    await state.clear()


@about_router.callback_query(SectionState.about, F.data == "Изменить")
async def about_info_to_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_data = await company_info_crud.get_multi(session)
    info_list = [info.name for info in about_data]
    await callback.message.edit_text(
        "Какую информацию вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(info_list, previous_menu=PREVIOUS_MENU),
    )
    await state.set_state(UpdateAboutInfo.select)


@about_router.callback_query(
    UpdateAboutInfo.select,
    and_f(
        F.data != "Название ссылки",
        F.data != "Адрес ссылки",
        F.data != PREVIOUS_MENU,
    ),
)
async def update_info_choise(callback: CallbackQuery, state: FSMContext):
    await state.update_data(select=callback.data)
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=await get_inline_keyboard(
            ["Название ссылки", "Адрес ссылки"], previous_menu=PREVIOUS_MENU
        ),
    )


@about_router.callback_query(UpdateAboutInfo.select, F.data == "Название ссылки")
async def about_name_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_name = await state.get_data()
    about_name_text = about_name.get("select")
    await callback.message.answer(
        f"Сейчас у ссылки такое название:\n\n {about_name_text}\n\n Введите новое название"
    )
    await state.set_state(UpdateAboutInfo.name)


@about_router.callback_query(UpdateAboutInfo.select, F.data == "Адрес ссылки")
async def about_url_update(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    about_name_data = await state.get_data()
    about_name_text = about_name_data.get("select")
    about_info = await company_info_crud.get_by_about_name(about_name_text, session)
    await callback.message.answer(
        f"Сейчас у ссылки такой адрес:\n\n {about_info.url}\n\n Введите новое название"
    )
    await state.set_state(UpdateAboutInfo.url)


@about_router.message(or_f(UpdateAboutInfo.name, UpdateAboutInfo.url), F.text)
async def update_about_info(message: Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    old_data = await state.get_data()
    old_about_data = await company_info_crud.get_by_about_name(
        old_data.get("select"), session
    )
    if current_state == UpdateAboutInfo.name:
        await state.update_data(name=message.text)
    elif current_state == UpdateAboutInfo.url:
        await state.update_data(url=message.text)
    update_data = await state.get_data()
    await company_info_crud.update(old_about_data, update_data, session)
    await message.answer(
        "Информация обновлена!",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
    await state.clear()
