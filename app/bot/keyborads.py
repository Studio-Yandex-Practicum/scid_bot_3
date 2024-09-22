from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# кнопку вернуться назад можно вынести отдельно, чтобы не дублировать код

PRODUCTS_AND_SERVICES = [
    'Разработка сайтов', 'Создание порталов',
    'Разработка мобильных приложений', 'Консультация по КИОСК365',
    '"НБП ЕЖА"', 'Хостинг',
]  # моделирую результат запроса из бд ( * )

LIST_OF_PROJECTS = ['Проект1', 'Проект2', 'Проект3']  # ( * )

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть портфолио.')],
        [KeyboardButton(text='Получить информацию о компании.')],
        [KeyboardButton(text='Узнать о продуктах и услугах.')],
        [KeyboardButton(text='Получить техническую поддержку.'),],
        [KeyboardButton(text='Связаться с менеджером.')],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder='Выберите пункт меню.'
)

company_information_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Презентация компании.',
                url='https://www.visme.co/ru/powerpoint-online/'  # тут ссылка на презентацию, ткунл рандомную
            )
        ],
        [
            InlineKeyboardButton(
                text='Карточка компании.',
                url='https://github.com/Rxyalxrd'  # тут будет карточка компании, пока моя)
            )
        ],
        [
            InlineKeyboardButton(
                text='Вернуться к основным вариантам.',
                callback_data='back_to_main_menu'
            )
        ]
    ]
)


async def inline_products_and_services():  # тут будем брать данные из бд
    """Инлайн клавиатура для продуктов и услуг."""  # аннатацию тоже не пишу пока

    keyboard = InlineKeyboardBuilder()

    for index, product_and_service in enumerate(PRODUCTS_AND_SERVICES):
        # callback_data = f"service_{index}"
        keyboard.add(InlineKeyboardButton(
            text=product_and_service,
            callback_data=f'service_{index}'
        ))

    keyboard.add(
        InlineKeyboardButton(
            text='Вернуться к основным вариантам.',
            callback_data='back_to_main_menu'
        )
    )

    return keyboard.adjust(1).as_markup()


company_portfolio_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Перейти к проектам.',
                callback_data='show_projects'
            )
        ],
        [
            InlineKeyboardButton(
                text='Вернуться к основным вариантам.',
                callback_data='back_to_main_menu'
            )
        ]
    ]
)


async def list_of_projects_keyboard():  # данные будут в бд
    """Инлайн вывод проектов."""

    keyboard = InlineKeyboardBuilder()

    for project in LIST_OF_PROJECTS:
        keyboard.add(InlineKeyboardButton(
            text=project,
            url='https://github.com/'  # тут будут ссылки, берем из бд
        ))

    keyboard.add(
        InlineKeyboardButton(
            text='Вернуться к основным вариантам.',
            callback_data='back_to_main_menu'
        )
    )

    return keyboard.adjust(1).as_markup()


support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='F.A.Q',
                callback_data='get_faq'
            )
        ],
        [
            InlineKeyboardButton(
                text='Проблемы с продуктами',
                callback_data='get_problems_with_products'
            )
        ],
        [
            InlineKeyboardButton(
                text='Запрос на обратный звонок',
                callback_data='callback_request'
            )
        ],
        [
            InlineKeyboardButton(
                text='Вернуться к основным вариантам.',
                callback_data='back_to_main_menu'
            )
        ]
    ]
)
