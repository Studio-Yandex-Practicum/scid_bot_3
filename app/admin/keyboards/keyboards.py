from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineKeyboardManager:
    """
    Менеджер для создания инлайн-клавиатур.

    Этот класс позволяет добавлять кнопки, включая кнопки для администраторов
    и кнопку "Назад".
    """

    def __init__(
        self,
        options=None,
        callback=None,
        urls=None,
        size=(1,),
        previous_menu=None,
        admin_update_menu=None,
    ):
        self.options = options if options is not None else []
        self.callback = callback if callback is not None else self.options
        self.urls = urls if urls is not None else []
        self.size = size
        self.previous_menu = previous_menu
        self.admin_update_menu = admin_update_menu
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

    def add_back_button(self):
        """Добавить кнопку 'Назад'."""
        if self.previous_menu:
            self.keyboard.add(
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=self.previous_menu,
                )
            )

    def add_admin_button(self):
        """Добавить кнопку 'Редактировать' для администраторов."""
        if self.admin_update_menu:
            self.keyboard.add(
                InlineKeyboardButton(
                    text="Редактировать🔧",
                    callback_data=f"{self.admin_update_menu}_",
                )
            )

    def create_keyboard(self) -> InlineKeyboardMarkup:
        """Создать клавиатуру и вернуть ее."""
        self.add_buttons()
        self.add_back_button()
        self.add_admin_button()
        return self.keyboard.adjust(*self.size).as_markup(resize_keyboard=True)


async def get_inline_keyboard(
    options=None,
    callback=None,
    urls=None,
    previous_menu=None,
    admin_update_menu=None,
):
    """Создать базовую инлайн-клавиатуру.

    :param options: Список названий кнопок.
    :param callback: Список коллбек-данных для кнопок.
    :param urls: Список URL для кнопок.
    :param previous_menu: Коллбек-данные для кнопки "Назад".
    :return: Объект InlineKeyboardMarkup.
    """
    return InlineKeyboardManager(
        options=options,
        callback=callback,
        urls=urls,
        previous_menu=previous_menu,
        admin_update_menu=admin_update_menu,
    ).create_keyboard()


async def get_delete_message_keyboard() -> InlineKeyboardMarkup:
    """Создать копку для удаления сообщения."""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Понятно! :)", callback_data="delete")
    )
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def get_inline_confirmation(
    cancel_option: str,
    option: str = "Да",
) -> InlineKeyboardMarkup:
    """Кнопка для подтверждения действий."""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Да", callback_data=option))
    keyboard.add(InlineKeyboardButton(text="Нет", callback_data=cancel_option))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)
