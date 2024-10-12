# from typing import Any
# from app.admin.keyboards.keyboards import InlineKeyboardManager

# from aiogram.types import (
#     InlineKeyboardButton,
#     InlineKeyboardMarkup,
# )
# from aiogram.utils.keyboard import InlineKeyboardBuilder

# keyboard = InlineKeyboardManager()
# keyboard.add_previous_menu_button(previous_menu="NAZAD")


# test = keyboard.create_keyboard()

# # keyboard.add_admin_button("test")

# keyboard.add_extra_buttons(["test"])
# test2 = keyboard.create_keyboard()
# # print(vars(keyboard))
# keyboard.add_extra_buttons(["extra_test"])
# test3 = keyboard.create_keyboard()


def get_buttons_from_keyboard(keyboard):
    button_list = []
    for row in keyboard.inline_keyboard:
        for button in row:
            button_list.append((button.text, button.callback_data))
    return button_list


# keyboard.update_buttons(["updated_list"])
# test4 = keyboard.create_keyboard()
# print(get_buttons_from_keyboard(test))
# print(get_buttons_from_keyboard(test2))
# print(get_buttons_from_keyboard(test3))
# print(get_buttons_from_keyboard(test4))


# class InlineKeyboardManager:
#     def __init__(
#         self,
#         options=None,
#         callback=None,
#         urls=None,
#         size=(1,),
#         previous_menu=None,
#         admin_update_menu=None,
#     ):
#         self.options = options if options is not None else []
#         self.callback = callback if callback is not None else self.options
#         self.urls = urls if urls is not None else []
#         self.size = size
#         self.previous_menu = previous_menu
#         self.admin_update_menu = admin_update_menu
#         self.keyboard = InlineKeyboardBuilder()

#     def add_buttons(self):
#         """Добавить основные кнопки в клавиатуру."""
#         for index, option in enumerate(self.options):
#             self.keyboard.add(
#                 InlineKeyboardButton(
#                     text=option,
#                     callback_data=str(self.callback[index]),
#                     url=(
#                         self.urls[index]
#                         if self.urls and index < len(self.urls)
#                         else None
#                     ),
#                 )
#             )

#     def add_back_button(self):
#         """Добавить кнопку 'Назад'."""
#         if self.previous_menu:
#             self.keyboard.add(
#                 InlineKeyboardButton(
#                     text="Назад",
#                     callback_data=self.previous_menu,
#                 )
#             )

#     def add_admin_button(self):
#         """Добавить кнопку 'Редактировать' для администраторов."""
#         self.keyboard.add(
#             InlineKeyboardButton(
#                 text="Редактировать🔧",
#                 callback_data=f"{self.admin_update_menu}_",
#             )
#         )

#     def create_keyboard(self) -> InlineKeyboardMarkup:
#         """Создать клавиатуру и вернуть ее.

#         :return: Объект InlineKeyboardMarkup с добавленными кнопками.
#         """
#         self.add_buttons()
#         if self.previous_menu:
#             self.add_back_button()
#         if self.admin_update_menu:
#             self.add_admin_button
#         return self.keyboard.adjust(*self.size).as_markup(resize_keyboard=True)


# def get_base_inline_keyboard(
#     options=None,
#     callback=None,
#     urls=None,
#     previous_menu=None,
# ):
#     return InlineKeyboardManager(
#         options=options,
#         callback=callback,
#         urls=urls,
#         previous_menu=previous_menu,
#     ).create_keyboard()


# def get_admin_keyboard(
#     admin_update_menu,
#     options=None,
#     callback=None,
#     urls=None,
#     previous_menu=None,
# ):
#     return InlineKeyboardManager(
#         options=options,
#         callback=callback,
#         urls=urls,
#         previous_menu=previous_menu,
#         admin_update_menu=admin_update_menu,
#     ).create_keyboard()


# class AdminInlineKeyboard(BaseInlineKeyboardManager):
#     """
#     Класс для управления инлайн-клавиатурами с администраторскими функциями.

#     Этот класс наследует базовый класс и добавляет возможность
#     добавления кнопки "Редактировать" для администраторов.
#     """

#     def __init__(
#         self,
#         admin_update_menu: str,
#         *args,
#         **kwargs,
#     ):
#         self.admin_update_menu = admin_update_menu
#         super().__init__(*args, **kwargs)

#     def add_admin_button(self):
#         """Добавить кнопку 'Редактировать' для администраторов."""
#         self.keyboard.add(
#             InlineKeyboardButton(
#                 text="Редактировать🔧",
#                 callback_data=f"{self.admin_update_menu}_",
#             )
#         )

#     def create_keyboard(self) -> InlineKeyboardMarkup:
#         """Создать клавиатуру и вернуть ее.

#         :return: Объект InlineKeyboardMarkup с добавленными кнопками,
#                  включая кнопку "Редактировать".
#         """
#         super().create_keyboard()
#         self.add_admin_button()
#         return self.keyboard


# def get_base_inline_keyboard(options=None, callback=None, urls=None):
#     """Создать базовую инлайн-клавиатуру.

#     :param options: Список названий кнопок.
#     :param callback: Список коллбек-данных для кнопок.
#     :param urls: Список URL для кнопок.
#     :return: Объект InlineKeyboardMarkup.
#     """
#     return BaseInlineKeyboardManager(
#         options, callback=callback, urls=urls
#     ).create_keyboard()


# def get_admin_inline_kb(
#     admin_update_menu,
#     options=None,
#     callback=None,
#     urls=None,
#     previous_menu=None,
# ):
#     """Создать инлайн-клавиатуру для администраторов.

#     :param admin_update_menu: Коллбек-данные для кнопки "Редактировать".
#     :param options: Список названий кнопок.
#     :param callback: Список коллбек-данных для кнопок.
#     :param urls: Список URL для кнопок.
#     :param previous_menu: Коллбек-данные для кнопки "Назад".
#     :return: Объект InlineKeyboardMarkup.
#     """
#     return AdminInlineKeyboard(
#         admin_update_menu=admin_update_menu,
#         options=options,
#         callback=callback,
#         urls=urls,
#         previous_menu=previous_menu,
#     ).create_keyboard()

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
        self.add_admin_button()  # Исправлено: добавлены скобки
        return self.keyboard.adjust(*self.size).as_markup(resize_keyboard=True)


def get_base_inline_keyboard(
    options=None,
    callback=None,
    urls=None,
    previous_menu=None,
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
    ).create_keyboard()


def get_admin_keyboard(
    admin_update_menu,
    options=None,
    callback=None,
    urls=None,
    previous_menu=None,
):
    """Создать инлайн-клавиатуру для администраторов.

    :param admin_update_menu: Коллбек-данные для кнопки "Редактировать".
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
