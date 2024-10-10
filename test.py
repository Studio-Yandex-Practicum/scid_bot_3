class QuestionManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ask_question_to_delete(
        self, callback: CallbackQuery, state: FSMContext
    ):
        current_state = await state.get_state()
        await state.set_state(DeleteQuestion.question_type)
        await state.update_data(
            question_type=await set_question_type(current_state)
        )
        question_type = (await state.get_data()).get("question_type")
        question_list = await get_question_list(question_type, self.session)
        await callback.message.edit_text(
            "Какой вопрос удалить?",
            reply_markup=await get_inline_keyboard(
                question_list, previous_menu=PREVIOUS_MENU
            ),
        )
        await state.set_state(DeleteQuestion.question)

    async def confirm_delete_question(
        self, callback: CallbackQuery, state: FSMContext
    ):
        question = await info_crud.get_by_question_text(
            callback.data, self.session
        )
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить этот вопрос?\n\n {question.question}",
            reply_markup=await get_inline_confirmation_keyboard(
                option=question.question, cancel_option=PREVIOUS_MENU
            ),
        )
        await state.set_state(DeleteQuestion.confirm)

    async def delete_question(
        self, callback: CallbackQuery, state: FSMContext
    ):
        await state.clear()
        question = await info_crud.get_by_question_text(
            callback.data, self.session
        )
        await info_crud.remove(question, self.session)
        await callback.message.edit_text(
            "Вопрос удален!",
            reply_markup=await get_inline_keyboard(
                previous_menu=question.question_type
            ),
        )


# Использование в роутере
@info_router.callback_query(
    or_f(SectionState.faq, SectionState.troubleshooting), F.data == "Удалить"
)
async def handle_delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    manager = QuestionManager(session)
    await manager.ask_question_to_delete(callback, state)


@info_router.callback_query(DeleteQuestion.question, F.data)
async def handle_confirm_delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    manager = QuestionManager(session)
    await manager.confirm_delete_question(callback, state)


@info_router.callback_query(DeleteQuestion.confirm, F.data != PREVIOUS_MENU)
async def handle_delete_question(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    manager = QuestionManager(session)
    await manager.delete_question(callback, state)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineKeyboardManager:
    def __init__(self, options=None, callback=None, urls=None, size=(1,)):
        self.options = options if options is not None else []
        self.callback = callback if callback is not None else self.options
        self.urls = urls if urls is not None else []
        self.size = size
        self.keyboard = InlineKeyboardBuilder()

    def add_buttons(self):
        """Добавить основные кнопки в клавиатуру."""
        for index, option in enumerate(self.options):
            self.keyboard.add(
                InlineKeyboardButton(
                    text=option,
                    callback_data=str(self.callback[index]),
                    url=(
                        self.urls[index]
                        if self.urls and index < len(self.urls)
                        else None
                    ),
                )
            )

    def add_previous_menu_button(self, previous_menu):
        """Добавить кнопку 'Назад'."""
        self.keyboard.add(
            InlineKeyboardButton(
                text="Назад",
                callback_data=previous_menu,
            )
        )

    def add_admin_button(self, admin_update_menu):
        """Добавить кнопку 'Редактировать' для администраторов."""
        self.keyboard.add(
            InlineKeyboardButton(
                text="Редактировать🔧",
                callback_data=f"{admin_update_menu}_",
            )
        )

    def create_keyboard(self) -> InlineKeyboardMarkup:
        """Создать клавиатуру и вернуть ее."""
        self.add_buttons()
        return self.keyboard.adjust(*self.size).as_markup(resize_keyboard=True)


# Пример использования
async def get_inline_keyboard(options, callback=None, urls=None, size=(1,)):
    manager = InlineKeyboardManager(options, callback, urls, size)
    return manager.create_keyboard()


# Использование с добавлением дополнительных кнопок
async def get_custom_keyboard(
    options, previous_menu=None, is_admin=False, admin_update_menu=None
):
    manager = InlineKeyboardManager(options)
    manager.add_buttons()

    if previous_menu:
        manager.add_previous_menu_button(previous_menu)

    if is_admin and admin_update_menu:
        manager.add_admin_button(admin_update_menu)

    return manager.create_keyboard()
