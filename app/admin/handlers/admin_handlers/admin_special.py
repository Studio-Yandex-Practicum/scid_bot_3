from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.keyboards.keyboards import (
    get_inline_keyboard,
)
from admin.admin_settings import (
    ADMIN_SPECIAL_BUTTONS,
    ADMIN_SPECIAL_OPTIONS,
    DATETIME_FORMAT,
    MAIN_MENU_OPTIONS,
    MAIN_MENU_TEXT,
)
from models.models import ContactManager
from crud.request_to_manager import (
    close_case,
    get_all_manager_requests,
    get_all_support_requests,
    get_request,
)

admin_special_router = Router()
admin_special_router.message.filter(
    ChatTypeFilter(["private"]), IsManagerOrAdmin()
)


class RequestState(StatesGroup):
    manager_request = State()
    support_request = State()


async def get_state_name(state: str) -> str:
    """Получить название состояния и вернуть его название."""
    state_name = state.split(":")[1]
    return ADMIN_SPECIAL_OPTIONS.get(state_name)


async def get_requests_list(
    request_list: list[ContactManager],
) -> tuple[list[str]]:
    options = [
        (
            f"Заявка номер {request.id} от "
            f"{request.shipping_date.strftime(DATETIME_FORMAT)}"
        )
        for request in request_list
    ]
    request_ids = [request.id for request in request_list]
    return options, request_ids


@admin_special_router.callback_query(
    F.data == MAIN_MENU_OPTIONS.get("admin_special")
)
async def get_admin_special_options(callback: CallbackQuery):
    await callback.message.edit_text(
        "Дополнительная информация для администрации:",
        reply_markup=await get_inline_keyboard(
            ADMIN_SPECIAL_BUTTONS, previous_menu=MAIN_MENU_TEXT
        ),
    )


@admin_special_router.callback_query(
    F.data == ADMIN_SPECIAL_OPTIONS.get("manager_request")
)
async def get_manager_request_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить список заявок на обратный звонок от менеджера."""
    request_list = await get_all_manager_requests(session)
    options, callbacks = await get_requests_list(request_list)
    await callback.message.edit_text(
        ADMIN_SPECIAL_OPTIONS.get("manager_request"),
        reply_markup=await get_inline_keyboard(
            options=options,
            callback=callbacks,
            previous_menu=MAIN_MENU_OPTIONS.get("admin_special"),
        ),
    )
    await state.set_state(RequestState.manager_request)


@admin_special_router.callback_query(
    F.data == ADMIN_SPECIAL_OPTIONS.get("support_request")
)
async def get_support_request_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить список заявок на техподдержку."""
    request_list = await get_all_support_requests(session)
    options, callbacks = await get_requests_list(request_list)
    await callback.message.edit_text(
        ADMIN_SPECIAL_OPTIONS.get("support_request"),
        reply_markup=await get_inline_keyboard(
            options=options,
            callback=callbacks,
            previous_menu=MAIN_MENU_OPTIONS.get("admin_special"),
        ),
    )
    await state.set_state(RequestState.support_request)


@admin_special_router.callback_query(RequestState(), F.data.isnumeric())
async def get_request_data(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить данные о заявке."""
    current_state = await state.get_state()
    back_option = await get_state_name(current_state)
    request = await get_request(callback.data, session)
    message = (
        f"Заявка от пользователя {request.first_name}\n\n"
        f"Номер для связи: {request.phone_number}\n\n"
        f"Дата заявки: {request.shipping_date.strftime(DATETIME_FORMAT)}\n\n"
    )
    await callback.message.edit_text(
        message,
        reply_markup=await get_inline_keyboard(
            ["Закрыть"], previous_menu=back_option
        ),
    )
    await state.update_data(request_id=callback.data)


@admin_special_router.callback_query(RequestState(), F.data == "Закрыть")
async def close_request(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Закрыть заявку."""
    try:
        current_state = await state.get_state()
        back_option = await get_state_name(current_state)
        fsm_data = await state.get_data()
        request_id = fsm_data.get("request_id")
        await close_case(request_id, session)
        await callback.message.edit_text(
            "Заявка закрыта!",
            reply_markup=await get_inline_keyboard(previous_menu=back_option),
        )
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {e}")
