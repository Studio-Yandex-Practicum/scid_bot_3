from aiogram.types import (
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_paginated_keyboard_size(items_per_page: int):
    """Вернуть кортеж вида (1, 1, ... 1, 2, 1)"""

    return (1,) * items_per_page + (2, 1)


async def get_inline_keyboard(
    options: list[str] | str | None = None,
    callback: list[str] | str | None = None,
    previous_menu: str | None = None,
    urls: list[str] | None = None,
    size: tuple[int] = (1,),
    is_admin: bool | None = False,
    admin_update_menu: str | None = None,
) -> InlineKeyboardMarkup:
    """Создать набор кнопок для меню раздела."""

    keyboard = InlineKeyboardBuilder()

    if not callback:
        callback = options

    if options:
        for index, option in enumerate(options):
            keyboard.add(
                InlineKeyboardButton(
                    text=option,
                    callback_data=str(callback[index]),
                    url=(
                        urls[index]
                        if urls and index in range(len(urls))
                        else None
                    ),
                )
            )

    if previous_menu:
        keyboard.add(
            InlineKeyboardButton(
                text="Назад",
                callback_data=previous_menu,
            )
        )

    if is_admin:
        keyboard.add(
            InlineKeyboardButton(
                text="Редактировать🔧",
                callback_data=f"{admin_update_menu}_",
            )
        )

    return keyboard.adjust(*size).as_markup(resize_keyboard=True)


# async def get_inline_paginated_keyboard(
#     options: Optional[Union[list[str], str]] = None,
#     pagination: dict = None,
#     size: tuple[int] = (1,),
# ) -> InlineKeyboardMarkup:
#     """Создать набор кнопок для меню раздела с поддержкой пагинации."""
#     keyboard = InlineKeyboardBuilder()
#     total_pages = 0
#     current_page = 0
#     if pagination:
#         current_page = pagination.get("current_page", 1)
#         items_per_page = pagination.get("items_per_page", 5)
#         total_items = len(options) if options else 0
#         total_pages = (total_items + items_per_page - 1) // items_per_page

#         start_index = (current_page - 1) * items_per_page
#         end_index = min(start_index + items_per_page, total_items)

#         current_options = options[start_index:end_index] if options else []
#     else:
#         current_options = options

#     for option in current_options:
#         keyboard.add(
#             InlineKeyboardButton(
#                 text=option,
#                 callback_data=option,
#             ),
#         )
#     if total_pages > 1:
#         if current_page > 1:
#             keyboard.add(
#                 InlineKeyboardButton(
#                     text="◀️ Предыдущая",
#                     callback_data=f"{current_page - 1}",
#                 )
#             )
#         if current_page < total_pages:
#             keyboard.add(
#                 InlineKeyboardButton(
#                     text="Следующая ▶️",
#                     callback_data=f"{current_page + 1}",
#                 )
#             )
#         keyboard.add(
#             InlineKeyboardButton(
#                 text="Главное меню",
#                 callback_data=BASE_BUTTONS.get("main_menu"),
#             )
#         )

#     return keyboard.adjust(*size).as_markup(resize_keyboard=True)


async def get_inline_paginated_keyboard(
    options: list[str] | str | None = None,
    callback: list[str] | str | None = None,
    previous_menu: str | None = None,
    previous_menu_text: str | None = "Назад",
    items_per_page: int = 5,
    size: tuple[int] = (1,),
    current_page: int = 1,
) -> InlineKeyboardMarkup:
    """Создать набор кнопок для меню раздела с поддержкой пагинации."""

    if not callback:
        callback = options

    keyboard = InlineKeyboardBuilder()

    total_pages = 0
    total_items = len(options) if options else 0
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_index = (current_page - 1) * items_per_page
    end_index = min(start_index + items_per_page, total_items)
    current_options = options[start_index:end_index] if options else []

    for index, option in enumerate(current_options):
        keyboard.add(
            InlineKeyboardButton(
                text=option,
                callback_data=str(callback[index]),
            ),
        )

    navigation_row = []
    if total_pages > 1:
        if current_page > 1:
            navigation_row.append(
                InlineKeyboardButton(
                    text="◀️ Предыдущая",
                    callback_data=f"page:{current_page - 1}",
                )
            )

        if current_page < total_pages:
            navigation_row.append(
                InlineKeyboardButton(
                    text="Следующая ▶️",
                    callback_data=f"page:{current_page + 1}",
                )
            )

        if navigation_row:
            keyboard.add(*navigation_row)
        keyboard.add(
            InlineKeyboardButton(
                text=previous_menu_text,
                callback_data=previous_menu,
            )
        )

    return keyboard.adjust(*size).as_markup(resize_keyboard=True)


async def get_reply_keyboard(
    options: list[str] | str | None = None,
    size: tuple[int] = (1,),
) -> ReplyKeyboardMarkup:
    """Создать экранную клавиатуру."""

    keyboard = ReplyKeyboardBuilder()

    if options:
        if isinstance(options, list):
            for option in options:
                keyboard.add(KeyboardButton(text=option, callback_data=option))
        else:
            keyboard.add(
                KeyboardButton(
                    text=options,
                    # callback_data=options,
                )
            )

    return keyboard.adjust(*size).as_markup()


async def get_delete_message_keyboard() -> InlineKeyboardMarkup:
    """Создать копку для удаления сообщения."""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Понятно! :)", callback_data="delete")
    )
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def get_inline_confirmation_keyboard(
    option: str, cancel_option: str
) -> InlineKeyboardMarkup:
    """Кнопка для подтверждения действий."""

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Да", callback_data=option))
    keyboard.add(InlineKeyboardButton(text="Нет", callback_data=cancel_option))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)
