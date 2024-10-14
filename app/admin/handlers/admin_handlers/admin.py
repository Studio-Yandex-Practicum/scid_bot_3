from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from admin.filters.filters import ChatTypeFilter, IsManagerOrAdmin
from admin.keyboards.keyboards import (
    get_inline_keyboard,
)
from admin.admin_settings import (
    ADMIN_BASE_KEYBOARD,
    MAIN_MENU_BUTTONS,
    MAIN_MENU_OPTIONS,
    ADMIN_PORTFOLIO_KEYBOARD,
    PORTFOLIO_BUTTONS,
    PORTFOLIO_MENU_OPTIONS,
    SUPPORT_OPTIONS,
    SUPPROT_MENU_BUTTONS,
)


admin_main_router = Router()
admin_main_router.message.filter(
    ChatTypeFilter(["private"]), IsManagerOrAdmin()
)


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

    general_questions = State()
    problems_with_products = State()
    portfolio = State()
    other_projects = State()
    about = State()
    product = State()
    callback_request = State()
    category = State()

    @classmethod
    def get_condition(cls, menu_text: str):
        """Выбрать категорию для раздела."""

        if menu_text == SUPPORT_OPTIONS.get("general_questions"):
            return cls.general_questions
        elif menu_text == SUPPORT_OPTIONS.get("problems_with_products"):
            return cls.problems_with_products
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
async def update_section_data(callback: CallbackQuery, state: FSMContext):
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
