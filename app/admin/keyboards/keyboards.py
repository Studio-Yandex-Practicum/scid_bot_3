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
        """Добавить кнопку 'Вернуться'."""
        if self.previous_menu:
            self.keyboard.add(
                InlineKeyboardButton(
                    text="Вернуться",
                    callback_data=self.previous_menu,
                )
            )

    def add_admin_button(self):
        """Добавить кнопку 'Редактировать' для администраторов."""
        if self.admin_update_menu:
            self.keyboard.row(
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


class PaginatedInlineKeyboardManager(InlineKeyboardManager):
    """
    Менеджер для создания инлайн-клавиатур с поддержкой пагинации.
    """

    def __init__(
        self,
        options=None,
        callback=None,
        urls=None,
        size=[
            1,
        ],
        previous_menu=None,
        admin_update_menu=None,
        items_per_page=5,
    ):
        super().__init__(
            options, callback, urls, size, previous_menu, admin_update_menu
        )
        self.items_per_page = items_per_page

    def create_keyboard(self, page=0) -> InlineKeyboardMarkup:
        """Создать клавиатуру с учетом пагинации и вернуть ее."""
        start_index = page * self.items_per_page
        end_index = start_index + self.items_per_page
        paginated_options = self.options[start_index:end_index]
        paginated_callbacks = self.callback[start_index:end_index]
        paginated_urls = self.urls[start_index:end_index]
        for index, option in enumerate(paginated_options):
            self.keyboard.add(
                InlineKeyboardButton(
                    text=option,
                    callback_data=str(paginated_callbacks[index]),
                    url=(paginated_urls[index] if paginated_urls else None),
                )
            )
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️Назад",
                    callback_data=f"page_{page - 1}",
                )
            )
        if end_index < len(self.options):
            nav_buttons.append(
                InlineKeyboardButton(
                    text="Далее▶️",
                    callback_data=f"page_{page + 1}",
                )
            )
        if nav_buttons:
            self.keyboard.row(*nav_buttons)
        self.add_back_button()
        size_list = (
            [1] * self.items_per_page + [2]
            if page > 0 and page < end_index
            else [1]
        )
        self.size = size_list

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


async def get_paginated_inline_keyboard(
    options=None,
    callback=None,
    urls=None,
    previous_menu=None,
    admin_update_menu=None,
    items_per_page=5,
    page=0,
):
    """Создать инлайн-клавиатуру с пагинацией.

    :param options: Список названий кнопок.
    :param callback: Список коллбек-данных для кнопок.
    :param urls: Список URL для кнопок.
    :param previous_menu: Коллбек-данные для кнопки "Назад".
    :param items_per_page: Количество кнопок на одной странице.
    :param page: Номер текущей страницы.
    :return: Объект InlineKeyboardMarkup.
    """
    return PaginatedInlineKeyboardManager(
        options=options,
        callback=callback,
        urls=urls,
        previous_menu=previous_menu,
        admin_update_menu=admin_update_menu,
        items_per_page=items_per_page,
    ).create_keyboard(page=page)


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
