import logging

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
    DATETIME_FORMAT,
    MAIN_MENU_OPTIONS,
    MAIN_MENU_TEXT,
    SUPERUSER_PROMOTION_BUTTONS,
    SUPERUSER_PROMOTION_OPTIONS,
    SUPERUSER_SPECIAL_BUTTONS,
    SUPERUSER_SPECIAL_OPTIONS,
)
from bot.exceptions import message_exception_handler
from models.models import User, RoleEnum
from crud.request_to_manager import get_manager_stats
from crud.user_crud import user_crud

logger = logging.getLogger(__name__)

superuser_router = Router()
superuser_router.message.filter(ChatTypeFilter(["private"]), IsAdminOnly())
superuser_router.callback_query.filter(IsAdminOnly())


PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("admin_special")

manager = State()


class RoleState(StatesGroup):
    manager = State()
    admin = State()
    user = State()
    name = State()


async def check_user_tg_id_data(
    tg_id: int, session: AsyncSession
) -> tuple[User, str | None]:
    """
    Проверить данные пользователя и вернуть пользователя и соообщение,
    если пользователь админ или такого пользователя нет в базе.
    """
    message_text = ""
    user: User = await user_crud.get_user_by_tg_id(tg_id, session)
    if not user:
        message_text = "Такого пользователя в базе нет!"
    elif user.role == RoleEnum.ADMIN:
        message_text = "Нельзя менять роль админа!"
    return user, message_text


@message_exception_handler(
    log_error_text="Ошибка при открытии меню суперпользователя"
)
@superuser_router.callback_query(
    F.data == MAIN_MENU_OPTIONS.get("admin_special")
)
async def get_admin_special_options(
    callback: CallbackQuery, state: FSMContext
):
    """Меню суперпользователя."""
    try:
        await state.clear()
        await callback.message.edit_text(
            "Дополнительная информация для администрации:",
            reply_markup=await get_inline_keyboard(
                SUPERUSER_SPECIAL_BUTTONS, previous_menu=MAIN_MENU_TEXT
            ),
        )
        logger.info(
            f"Пользователь {callback.from_user.id} открыл меню суперпользователя."
        )
    except Exception as e:
        await callback.message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )


@message_exception_handler(
    log_error_text="Ошибка при переходе в меню управления персоналом"
)
@superuser_router.callback_query(
    F.data == SUPERUSER_SPECIAL_OPTIONS.get("promotion")
)
async def get_superuser_options(callback: CallbackQuery):
    """Перейти в меню управления персоналом."""
    try:
        await callback.message.edit_text(
            SUPERUSER_SPECIAL_OPTIONS.get("promotion"),
            reply_markup=await get_inline_keyboard(
                SUPERUSER_PROMOTION_BUTTONS,
                previous_menu=PREVIOUS_MENU,
            ),
        )
        logger.info(
            f"Пользователь {callback.from_user.id} открыл меню управления персоналом."
        )
    except Exception as e:
        await callback.message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )


@message_exception_handler(
    log_error_text="Ошибка при получении списка менеджеров"
)
@superuser_router.callback_query(
    F.data == SUPERUSER_PROMOTION_OPTIONS.get("manager_list")
)
async def get_manager_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить список менеджеров."""
    try:
        manager_list = await user_crud.get_manager_list(session)
        managers_tg_ids = [manager.tg_id for manager in manager_list]
        managers_names = [manager.name for manager in manager_list]
        await callback.message.edit_text(
            SUPERUSER_PROMOTION_OPTIONS.get("manager_list"),
            reply_markup=await get_inline_keyboard(
                options=managers_names,
                callback=managers_tg_ids,
                previous_menu=PREVIOUS_MENU,
            ),
        )
        await state.set_state(manager)
        logger.info(
            f"Пользователь {callback.from_user.id} запросил список менеджеров."
        )
    except Exception as e:
        await callback.message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )


@message_exception_handler(
    log_error_text="Ошибка при получении информации о менеджере"
)
@superuser_router.callback_query(manager, F.data.isnumeric())
async def get_manager(callback: CallbackQuery, session: AsyncSession):
    """Получить информацию о менеджере."""
    try:
        manager = await user_crud.get_user_by_tg_id(callback.data, session)
        cases_count, last_case_closed = await get_manager_stats(
            callback.data, session
        )
        last_case_message = (
            (
                f"{last_case_closed.id} "
                f"{last_case_closed.shipping_date_close.strftime(DATETIME_FORMAT)}"
            )
            if last_case_closed
            else "закрытых заявок пока нет."
        )
        message_text = (
            f"{manager.role.__str__()} {manager.name}\n\n "
            f"Телеграм id: {manager.tg_id} \n\n"
            f"Количество закрытых заявок: {cases_count} \n\n"
            f"Номер и дата последней закрытой заявки: {last_case_message}"
        )
        await callback.message.edit_text(
            message_text,
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )
        logger.info(
            f"Пользователь {callback.from_user.id} запросил информацию о менеджере {manager.name}."
        )
    except Exception as e:
        await callback.message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )


@message_exception_handler(
    log_error_text="Ошибка при вводе Telegram ID для смены роли"
)
@superuser_router.callback_query(
    or_f(
        F.data == SUPERUSER_PROMOTION_OPTIONS.get("promote"),
        F.data == SUPERUSER_PROMOTION_OPTIONS.get("promote_to_admin"),
        F.data == SUPERUSER_PROMOTION_OPTIONS.get("demote"),
    )
)
async def get_user_id_for_action(callback: CallbackQuery, state: FSMContext):
    """Ввести телеграм id пользователя для смены роли."""
    try:
        if callback.data == SUPERUSER_PROMOTION_OPTIONS.get("promote"):
            await state.set_state(RoleState.manager)
            await state.update_data(role=RoleEnum.MANAGER)
        elif callback.data == SUPERUSER_PROMOTION_OPTIONS.get(
            "promote_to_admin"
        ):
            await state.set_state(RoleState.admin)
            await state.update_data(role=RoleEnum.ADMIN)
        elif callback.data == SUPERUSER_PROMOTION_OPTIONS.get("demote"):
            await state.set_state(RoleState.user)
            await state.update_data(role=RoleEnum.USER)
        await callback.message.edit_text(
            "Введите id телеграм-пользователя:",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )
        logger.info(
            f"Пользователь {callback.from_user.id} выбрал действие для смены роли."
        )
    except Exception as e:
        await callback.message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )


@message_exception_handler(
    log_error_text="Ошибка при добавлении имени для менеджера или админа"
)
@superuser_router.message(
    or_f(RoleState.manager, RoleState.admin), F.text.isnumeric()
)
async def add_name_to_manager(message: Message, state: FSMContext):
    """Добавить имя для менеджера или админа."""
    try:
        await state.update_data(tg_id=message.text)
        await state.set_state(RoleState.name)
        await message.answer(
            "Введите имя для сотрудника:",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )
        logger.info(
            f"Пользователь {message.text} готовится к назначению роли менеджера или админа."
        )
    except Exception as e:
        await message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )


@message_exception_handler(log_error_text="Ошибка при назначении менеджера")
@superuser_router.message(or_f(RoleState.user, RoleState.name), F.text)
async def check_user_and_make_him_manager(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Проверить пользователя и присвоить ему роль менеджера."""
    try:
        current_state = await state.get_state()
        fsm_data = await state.get_data()
        user_tg_id = fsm_data.get("tg_id", message.text)
        user_new_role = fsm_data.get("role")
        user, error_message = await check_user_tg_id_data(user_tg_id, session)
        if error_message:
            await message.answer(
                error_message,
                reply_markup=await get_inline_keyboard(
                    previous_menu=PREVIOUS_MENU
                ),
            )
        else:
            if current_state == RoleState.user:
                await user_crud.change_user_role(user, user_new_role, session)
            elif current_state == RoleState.name:
                await user_crud.change_user_role(
                    user, user_new_role, session, message.text
                )
            await message.answer(
                f"Новая роль пользователя {user.tg_id} - {user_new_role}",
                reply_markup=await get_inline_keyboard(
                    previous_menu=PREVIOUS_MENU
                ),
            )
            logger.info(
                f"Пользователю {user_tg_id} изменили роль на {user_new_role}."
            )
    except Exception as e:
        await message.answer(
            f"Произошла ошибка: {e}",
            reply_markup=await get_inline_keyboard(
                previous_menu=PREVIOUS_MENU
            ),
        )
