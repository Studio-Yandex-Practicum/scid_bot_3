from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from admin.filters.filters import ChatTypeFilter, IsAdminOnly
from admin.keyboards.keyboards import (
    get_inline_keyboard,
)
from admin.admin_settings import (
    MAIN_MENU_OPTIONS,
    MAIN_MENU_TEXT,
    SUPERUSER_PROMOTION_BUTTONS,
    SUPERUSER_PROMOTION_OPTIONS,
    SUPERUSER_SPECIAL_BUTTONS,
    SUPERUSER_SPECIAL_OPTIONS,
)
from models.models import User, RoleEnum
from crud.user_crud import user_crud

superuser_router = Router()
superuser_router.message.filter(
    ChatTypeFilter(["private"]), IsAdminOnly()
)

PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("admin_special")


class RoleState(StatesGroup):
    promote = State()
    demote = State()


@superuser_router.callback_query(
    F.data == MAIN_MENU_OPTIONS.get("admin_special")
)
async def get_admin_special_options(callback: CallbackQuery):
    await callback.message.edit_text(
        "Дополнительная информация для администрации:",
        reply_markup=await get_inline_keyboard(
            SUPERUSER_SPECIAL_BUTTONS, previous_menu=MAIN_MENU_TEXT
        ),
    )


@superuser_router.callback_query(
    F.data == SUPERUSER_SPECIAL_OPTIONS.get("promotion")
)
async def get_superuser_options(callback: CallbackQuery):
    """Перейти в меню управления персоналом."""
    await callback.message.edit_text(
        SUPERUSER_SPECIAL_OPTIONS.get("promotion"),
        reply_markup=await get_inline_keyboard(
            SUPERUSER_PROMOTION_BUTTONS,
            previous_menu=PREVIOUS_MENU,
        ),
    )


@superuser_router.callback_query(
    F.data == SUPERUSER_PROMOTION_OPTIONS.get("manager_list")
)
async def get_manager_list(callback: CallbackQuery, session: AsyncSession):
    """Получить список менеджеров."""
    manager_list = await user_crud.get_manager_list(session)
    managers_tg_ids = [manager.tg_id + "\n\n" for manager in manager_list]
    managers = "".join(managers_tg_ids) if managers_tg_ids else "Список пуст!"
    await callback.message.edit_text(
        managers,
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )


@superuser_router.callback_query(
    or_f(
        F.data == SUPERUSER_PROMOTION_OPTIONS.get("promote"),
        F.data == SUPERUSER_PROMOTION_OPTIONS.get("demote"),
    )
)
async def get_user_id_for_action(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Ввести телеграм id пользователя для смены роли."""
    if callback.data == SUPERUSER_PROMOTION_OPTIONS.get("promote"):
        await state.set_state(RoleState.promote)
    elif callback.data == SUPERUSER_PROMOTION_OPTIONS.get("demote"):
        await state.set_state(RoleState.demote)
    await callback.message.edit_text(
        "Введите id телеграм-пользователя:",
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )


@superuser_router.message(RoleState(), F.text.isnumeric())
async def change_user_role(
    message: Message, state: FSMContext, session: AsyncSession
):
    """
    Проверить наличие пользователя в базе.
    Проверить роль пользователя.
    Изменить роль пользователя
    """
    user: User = await user_crud.get_user_by_tg_id(message.text, session)
    if not user:
        message_text = "Такого пользователя в базе нет!"
    if user.role == RoleEnum.ADMIN:
        message_text = "Нельзя менять роль админа!"
    current_state = await state.get_state()
    if current_state == RoleState.promote.state:
        message_text = f"Пользователь {message.text} назначен менеджером!"
        await user_crud.promote_to_manager(user, session)
    elif current_state == RoleState.demote.state:
        message_text == (
            f"Позльователь {message.text} теперь просто пользователь!"
        )
        await user_crud.demote_to_user(user, session)
    await message.answer(
        message_text,
        reply_markup=await get_inline_keyboard(previous_menu=PREVIOUS_MENU),
    )
