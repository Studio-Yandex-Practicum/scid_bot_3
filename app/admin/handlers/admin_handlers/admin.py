from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from crud.feedback_crud import feedback_crud
from crud.user_crud import user_crud
from filters.filters import ChatTypeFilter, IsAdmin
from keyboards.keyboards import (
    get_inline_keyboard,
    get_inline_paginated_keyboard,
    get_paginated_keyboard_size,
)
from const import (
    ADMIN_BASE_KEYBOARD,
    ADMIN_BASE_REPLY_OPTIONS,
    BASE_BUTTONS,
    FEEDBACK_PAGINATION,
    MAIN_MENU_BUTTONS,
    MAIN_MENU_OPTIONS,
    ADMIN_PORTFOLIO_KEYBOARD,
    PORTFOLIO_BUTTONS,
    PORTFOLIO_MENU_OPTIONS,
    SUPPORT_OPTIONS,
    SUPPROT_MENU_BUTTONS,
    USER_CALLBACK_PAGINATION,
)


admin_main_router = Router()
admin_main_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class UserState(StatesGroup):
    callback = State()
    close_case = State()


class FeedbackState(StatesGroup):
    feedback_choice = State()
    new_feedbacks = State()
    all_feedbacks = State()
    mark_as_read = State()


class SectionState(StatesGroup):
    """State для определения раздела, в который вносятся измения."""

    faq = State()
    troubleshooting = State()
    portfolio = State()
    other_projects = State()
    about = State()
    product = State()
    callback_request = State()
    category = State()

    @classmethod
    def get_condition(cls, menu_text: str):
        """Выбрать категорию для раздела."""

        if menu_text == SUPPORT_OPTIONS.get("faq"):
            return cls.faq
        elif menu_text == SUPPORT_OPTIONS.get("troubleshooting"):
            return cls.troubleshooting
        elif menu_text == SUPPORT_OPTIONS.get("callback_request"):
            return cls.callback_request
        elif menu_text == MAIN_MENU_OPTIONS.get("company_bio"):
            return cls.about
        elif menu_text == MAIN_MENU_OPTIONS.get("products"):
            return cls.product
        elif menu_text == MAIN_MENU_OPTIONS.get("portfolio"):
            return cls.portfolio
        elif menu_text == PORTFOLIO_MENU_OPTIONS.get("other_projects"):
            return cls.other_projects
        else:
            return cls.category


@admin_main_router.callback_query(F.data.endswith("_"))
async def update_category(callback: CallbackQuery, state: FSMContext):
    """Админские кнопки для внесения изменений в разделы."""

    menu = callback.data.rstrip("_")

    if menu == MAIN_MENU_OPTIONS.get("portfolio"):
        admin_keyboard = ADMIN_PORTFOLIO_KEYBOARD
    elif (
        (menu not in MAIN_MENU_BUTTONS)
        and (menu not in SUPPROT_MENU_BUTTONS)
        and (menu not in PORTFOLIO_BUTTONS)
    ):
        menu = "Назад"
        admin_keyboard = ADMIN_BASE_KEYBOARD
    else:
        admin_keyboard = ADMIN_BASE_KEYBOARD

    await callback.message.edit_text(
        "Выберете действие:",
        reply_markup=await get_inline_keyboard(
            options=admin_keyboard, previous_menu=menu
        ),
    )

    await state.set_state(SectionState.get_condition(menu))


@admin_main_router.message(
    F.text == ADMIN_BASE_REPLY_OPTIONS.get("callback_case"),
)
async def get_callback_cases_from_text(
    message: Message, state: FSMContext, session: AsyncSession
):

    user_list = await user_crud.get_users_with_callback_request(session)
    users_by_name = [user.name for user in user_list]
    users_by_id = [user.id for user in user_list]

    await message.delete()
    await message.answer(
        "Список пользователей, ожидающих обратного звонка",
        reply_markup=await get_inline_paginated_keyboard(
            options=users_by_name,
            callback=users_by_id,
            items_per_page=USER_CALLBACK_PAGINATION,
            size=get_paginated_keyboard_size(USER_CALLBACK_PAGINATION),
            previous_menu=BASE_BUTTONS.get("main_menu"),
            previous_menu_text=BASE_BUTTONS.get("main_menu"),
        ),
    )

    await state.set_state(UserState.callback)


@admin_main_router.callback_query(UserState(), F.data.startswith("page:"))
async def get_callback_cases(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):

    user_list = await user_crud.get_users_with_callback_request(session)
    users_by_name = [user.name for user in user_list]
    users_by_id = [user.id for user in user_list]
    current_page = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "Список пользователей, ожидающих обратного звонка",
        reply_markup=await get_inline_paginated_keyboard(
            options=users_by_name,
            callback=users_by_id,
            items_per_page=USER_CALLBACK_PAGINATION,
            current_page=current_page,
            size=get_paginated_keyboard_size(USER_CALLBACK_PAGINATION),
            previous_menu=BASE_BUTTONS.get("main_menu"),
            previous_menu_text=BASE_BUTTONS.get("main_menu"),
        ),
    )

    await state.set_state(UserState.callback)


@admin_main_router.callback_query(
    UserState.callback, F.data != BASE_BUTTONS.get("main_menu")
)
async def user_callback_request_data(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Закрыть заявку на обратный звонок."""

    user = await user_crud.get(callback.data, session)

    await callback.message.edit_text(
        f"Пользователь: {user.name}\n\n Телефон: {user.phone}",
        reply_markup=await get_inline_keyboard(
            options=["Закрыть заявку", "Назад к списку"],
            callback=[callback.data, "page:1"],
        ),
    )

    await state.set_state(UserState.close_case)


@admin_main_router.callback_query(UserState.close_case, F.data)
async def close_case(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Закрыть заявку на обратный звонок."""

    user = await user_crud.get(callback.data, session)

    await user_crud.close_case(user, session)
    await callback.message.edit_text(
        "Заявка закрыта!",
        reply_markup=await get_inline_keyboard(
            ["Назад к списку"],
            callback=[
                "page:1",
            ],
        ),
    )

    await state.set_state(UserState.callback)


@admin_main_router.message(
    F.text == ADMIN_BASE_REPLY_OPTIONS.get("feedback"),
)
async def feedback_choice(message: Message, state: FSMContext):
    """Вывести выбор списка отзывов."""

    await message.delete()
    await message.answer(
        "Какие отзывы показать?",
        reply_markup=await get_inline_keyboard(
            options=[
                "Только новые отзывы",
                "Все отзывы",
                BASE_BUTTONS.get("main_menu"),
            ],
        ),
    )

    await state.set_state(FeedbackState.feedback_choice)


@admin_main_router.callback_query(
    F.data == ADMIN_BASE_REPLY_OPTIONS.get("feedback"),
)
async def feedback_choice_callback(callback: CallbackQuery, state: FSMContext):
    """Вывести выбор списка отзывов."""

    await callback.message.edit_text(
        "Какие отзывы показать?",
        reply_markup=await get_inline_keyboard(
            options=[
                "Только новые отзывы",
                "Все отзывы",
                BASE_BUTTONS.get("main_menu"),
            ],
        ),
    )

    await state.set_state(FeedbackState.feedback_choice)


@admin_main_router.callback_query(
    FeedbackState.feedback_choice,
    F.data == "Только новые отзывы",
)
async def get_unread_feedbacks(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):

    new_feedbacks = await feedback_crud.get_new_feedbacks(session)
    feedbacks_list = [
        f"Отзыв номер {feedback.id} от {feedback.feedback_date}"
        for feedback in new_feedbacks
    ]
    feedbacks_ids = [feedback.id for feedback in new_feedbacks]

    await callback.message.edit_text(
        "Только новые отзывы",
        reply_markup=await get_inline_paginated_keyboard(
            options=feedbacks_list,
            callback=feedbacks_ids,
            items_per_page=FEEDBACK_PAGINATION,
            size=get_paginated_keyboard_size(FEEDBACK_PAGINATION),
            previous_menu=ADMIN_BASE_REPLY_OPTIONS.get("feedback"),
        ),
    )

    await state.set_state(FeedbackState.new_feedbacks)


@admin_main_router.callback_query(
    or_f(
        FeedbackState.feedback_choice,
        FeedbackState.new_feedbacks,
        FeedbackState.mark_as_read,
    ),
    F.data.startswith("page:"),
)
async def get_paginated_unread_feedbacks(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):

    new_feedbacks = await feedback_crud.get_new_feedbacks(session)
    feedbacks_list = [
        f"Отзыв номер {feedback.id} от {feedback.feedback_date}"
        for feedback in new_feedbacks
    ]
    feedbacks_ids = [feedback.id for feedback in new_feedbacks]
    current_page = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "Только новые отзывы",
        reply_markup=await get_inline_paginated_keyboard(
            options=feedbacks_list,
            callback=feedbacks_ids,
            current_page=current_page,
            items_per_page=FEEDBACK_PAGINATION,
            size=get_paginated_keyboard_size(FEEDBACK_PAGINATION),
            previous_menu=ADMIN_BASE_REPLY_OPTIONS.get("feedback"),
        ),
    )

    await state.set_state(FeedbackState.new_feedbacks)


@admin_main_router.callback_query(
    FeedbackState.feedback_choice,
    F.data == "Все отзывы",
)
async def get_all_feedbacks(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):

    feedbacks = await feedback_crud.get_multi(session)
    feedbacks_list = [
        f"Отзыв номер {feedback.id} от {feedback.feedback_date}"
        for feedback in feedbacks
    ]
    feedbacks_ids = [feedback.id for feedback in feedbacks]

    await callback.message.edit_text(
        "Все отзывы",
        reply_markup=await get_inline_paginated_keyboard(
            options=feedbacks_list,
            callback=feedbacks_ids,
            items_per_page=FEEDBACK_PAGINATION,
            size=get_paginated_keyboard_size(FEEDBACK_PAGINATION),
            previous_menu=ADMIN_BASE_REPLY_OPTIONS.get("feedback"),
        ),
    )

    await state.set_state(FeedbackState.all_feedbacks)


@admin_main_router.callback_query(
    or_f(
        FeedbackState.feedback_choice,
        FeedbackState.all_feedbacks,
    ),
    F.data.startswith("page:"),
)
async def get_all_paginated_feedbacks(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):

    feedbacks = await feedback_crud.get_multi(session)
    feedbacks_list = [
        f"Отзыв номер {feedback.id} от {feedback.feedback_date}"
        for feedback in feedbacks
    ]
    feedbacks_ids = [feedback.id for feedback in feedbacks]
    current_page = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "Все отзывы",
        reply_markup=await get_inline_paginated_keyboard(
            options=feedbacks_list,
            callback=feedbacks_ids,
            current_page=current_page,
            items_per_page=FEEDBACK_PAGINATION,
            size=get_paginated_keyboard_size(FEEDBACK_PAGINATION),
            previous_menu=ADMIN_BASE_REPLY_OPTIONS.get("feedback"),
        ),
    )

    await state.set_state(FeedbackState.all_feedbacks)


@admin_main_router.callback_query(
    or_f(FeedbackState.all_feedbacks, FeedbackState.new_feedbacks),
    F.data != BASE_BUTTONS.get("main_menu"),
)
async def get_feedback(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    """Получить данные отзыва."""

    feedback = await feedback_crud.get(callback.data, session)
    feedback_data = (
        f"Отзыв от пользователя {feedback.author.name}:\n\n"
        f"{feedback.feedback_text}\n\n Дата: {feedback.feedback_date}"
    )

    if feedback.unread:
        await callback.message.edit_text(
            feedback_data,
            reply_markup=await get_inline_keyboard(
                options=["Отметить как прочитанный", "Обратно к отзывам"],
                callback=[feedback.id, "page:1"],
            ),
        )

        await state.set_state(FeedbackState.mark_as_read)
    else:
        await callback.message.edit_text(
            feedback_data,
            reply_markup=await get_inline_keyboard(
                options=[
                    "Обратно к отзывам",
                ],
                callback=[
                    "page:1",
                ],
            ),
        )


@admin_main_router.callback_query(FeedbackState.mark_as_read, F.data)
async def mark_as_read(callback: CallbackQuery, session: AsyncSession):

    feedback = await feedback_crud.get(callback.data, session)

    await feedback_crud.mark_as_read(feedback, session)
    await callback.message.edit_text(
        "Отзыв отмечен как прочитанный!",
        reply_markup=await get_inline_keyboard(
            options=[
                "Обратно к отзывам",
            ],
            callback=[
                "Только новые отзывы",
            ],
        ),
    )
