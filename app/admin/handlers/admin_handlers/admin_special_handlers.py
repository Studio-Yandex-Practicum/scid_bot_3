import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.keyboards.keyboards import (
    get_inline_keyboard,
    get_paginated_inline_keyboard,
)
from admin.admin_settings import (
    ADMIN_SPECIAL_BUTTONS,
    ADMIN_SPECIAL_OPTIONS,
    DATETIME_FORMAT,
    FEEDBACKS_PER_PAGE,
    MAIN_MENU_OPTIONS,
    MAIN_MENU_TEXT,
    REQUESTS_PER_PAGE,
)
from bot.exceptions import message_exception_handler
from models.models import ContactManager, Feedback
from crud.request_to_manager import (
    close_case,
    get_all_manager_requests,
    get_all_support_requests,
    get_request,
)
from crud import feedback_crud

logger = logging.getLogger(__name__)

admin_special_router = Router()
admin_special_router.message.filter(
    ChatTypeFilter(["private"]), IsManagerOrAdmin()
)
admin_special_router.callback_query.filter(IsManagerOrAdmin())

PREVIOUS_MENU = MAIN_MENU_OPTIONS.get("admin_special")


class FeedbackState(StatesGroup):
    feedback = State()


class RequestState(StatesGroup):
    manager_request = State()
    support_request = State()


async def get_state_name(state: str) -> str:
    """Получить название состояния и вернуть его название."""
    state_name = state.split(":")[1]
    return ADMIN_SPECIAL_OPTIONS.get(state_name)


async def get_requests_data(
    request_list: list[ContactManager],
) -> tuple[list[str]]:
    options = [
        f"Заявка номер {request.id} от {request.shipping_date.strftime(DATETIME_FORMAT)}"
        for request in request_list
    ]
    request_ids = [request.id for request in request_list]
    return options, request_ids


async def get_feedbacks_data(
    feedback_list: list[Feedback],
) -> tuple[list[str]]:
    options = [
        f"Отзыв {feedback.id} от {feedback.feedback_date.strftime(DATETIME_FORMAT)}"
        for feedback in feedback_list
    ]
    feedback_ids = [feedback.id for feedback in feedback_list]
    return options, feedback_ids


@message_exception_handler(
    log_error_text="Ошибка при открытии админского меню"
)
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
    logger.info(f"Пользователь {callback.from_user.id} открыл админское меню.")


async def display_requests_page(
    callback: CallbackQuery, options, callbacks, page, title
):
    keyboard = await get_paginated_inline_keyboard(
        options=options,
        callback=callbacks,
        items_per_page=REQUESTS_PER_PAGE,
        page=page,
        previous_menu=PREVIOUS_MENU,
    )
    await callback.message.edit_text(
        title,
        reply_markup=keyboard,
    )


@message_exception_handler(
    log_error_text="Ошибка при получении списка менеджерских заявок"
)
@admin_special_router.callback_query(
    F.data == ADMIN_SPECIAL_OPTIONS.get("manager_request")
)
async def get_manager_request_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    request_list = await get_all_manager_requests(session)
    options, callbacks = await get_requests_data(request_list)
    current_page = 0
    await display_requests_page(
        callback,
        options,
        callbacks,
        current_page,
        ADMIN_SPECIAL_OPTIONS.get("manager_request"),
    )
    await state.set_state(RequestState.manager_request)
    logger.info(
        f"Пользователь {callback.from_user.id} запросил список менеджерских заявок."
    )


@message_exception_handler(
    log_error_text="Ошибка при получении списка заявок на техподдержку"
)
@admin_special_router.callback_query(
    F.data == ADMIN_SPECIAL_OPTIONS.get("support_request")
)
async def get_support_request_list(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    request_list = await get_all_support_requests(session)
    options, callbacks = await get_requests_data(request_list)
    current_page = 0
    await display_requests_page(
        callback,
        options,
        callbacks,
        current_page,
        ADMIN_SPECIAL_OPTIONS.get("support_request"),
    )
    await state.set_state(RequestState.support_request)
    logger.info(
        f"Пользователь {callback.from_user.id} запросил список заявок на техподдержку."
    )


@message_exception_handler(
    log_error_text="Ошибка при получении данных о заявке"
)
@admin_special_router.callback_query(RequestState(), F.data.isnumeric())
async def get_request_data(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
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
    logger.info(
        f"Пользователь {callback.from_user.id} запросил данные по заявке {request.id}."
    )


@message_exception_handler(log_error_text="Ошибка при закрытии заявки")
@admin_special_router.callback_query(RequestState(), F.data == "Закрыть")
async def close_request(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    current_state = await state.get_state()
    back_option = await get_state_name(current_state)
    fsm_data = await state.get_data()
    request_id = fsm_data.get("request_id")
    await close_case(callback.from_user.id, request_id, session)
    await callback.message.edit_text(
        "Заявка закрыта!",
        reply_markup=await get_inline_keyboard(previous_menu=back_option),
    )
    logger.info(
        f"Пользователь {callback.from_user.id} закрыл заявку {request_id}."
    )


@message_exception_handler(log_error_text="Ошибка при получении отзывов")
@admin_special_router.callback_query(
    F.data == ADMIN_SPECIAL_OPTIONS.get("feedbacks")
)
async def get_feedbacks(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    feedbacks = await feedback_crud.get_multi(session)
    options, callbacks = await get_feedbacks_data(feedbacks)
    current_page = 0
    await display_feedbacks_page(callback, options, callbacks, current_page)
    await state.set_state(FeedbackState.feedback)
    logger.info(f"Пользователь {callback.from_user.id} запросил все отзывы.")


async def display_feedbacks_page(
    callback: CallbackQuery, options, callbacks, page
):
    keyboard = await get_paginated_inline_keyboard(
        options=options,
        callback=callbacks,
        items_per_page=FEEDBACKS_PER_PAGE,
        page=page,
        previous_menu=PREVIOUS_MENU,
    )
    await callback.message.edit_text(
        ADMIN_SPECIAL_OPTIONS.get("feedbacks"),
        reply_markup=keyboard,
    )


@admin_special_router.callback_query(F.data.startswith("page_"))
async def handle_page_navigation(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    page = int(callback.data.split("_")[1])

    if FeedbackState.feedback.state == await state.get_state():
        feedbacks = await feedback_crud.get_multi(session)
        options, callbacks = await get_feedbacks_data(feedbacks)
        await display_feedbacks_page(callback, options, callbacks, page)

    elif RequestState.manager_request.state == await state.get_state():
        request_list = await get_all_manager_requests(session)
        options, callbacks = await get_requests_data(request_list)
        await display_requests_page(
            callback,
            options,
            callbacks,
            page,
            ADMIN_SPECIAL_OPTIONS.get("manager_request"),
        )

    elif RequestState.support_request.state == await state.get_state():
        request_list = await get_all_support_requests(session)
        options, callbacks = await get_requests_data(request_list)
        await display_requests_page(
            callback,
            options,
            callbacks,
            page,
            ADMIN_SPECIAL_OPTIONS.get("support_request"),
        )


@message_exception_handler(
    log_error_text="Ошибка при получении содержания отзыва"
)
@admin_special_router.callback_query(
    FeedbackState.feedback, F.data.isnumeric()
)
async def get_feedback_content(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    feedback = await feedback_crud.get(callback.data, session)
    message_text = (
        f"{feedback.feedback_text} \n\n Оценка: {feedback.rating} \n\n"
        f"Дата отзыва: {feedback.feedback_date.strftime(DATETIME_FORMAT)}"
    )
    await callback.message.edit_text(
        message_text,
        reply_markup=await get_inline_keyboard(
            previous_menu=ADMIN_SPECIAL_OPTIONS.get("feedbacks")
        ),
    )
    await state.clear()
    logger.info(
        f"Пользователь {callback.from_user.id} запросил содержание отзыва {feedback.id}."
    )
