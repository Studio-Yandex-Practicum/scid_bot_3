from aiogram.fsm.state import StatesGroup, State


ADMIN_POSITIVE_ANSWER: str = 'Добро пожаловать в админку!'

ADMIN_NEGATIVE_ANSWER: str = 'У вас нет прав администратора!'

START_MESSAGE: str = (
    'Здравстуйте! Я ваш виртуальный помощник. '
    'Как я могу помочь вам сегодня? '
)

MESSAGE_FOR_SHOW_PROJECTS: str = (
    'Вот некоторые из наших проектов. '
    'Выберите, чтобы узнать больше о каждом из них: '
)

MESSAGE_FOR_PREVIOUS_CHOICE: str = (
    'Вы вернулись в оснвное меню. '
    'Как я могу помочь вам дальше? '
)

MESSAGE_FOR_GET_QUESTIONS: str = 'Какой вид технической поддержки вам нужен? '

QUESTION_NOT_FOUND: str = 'Вопрос не найден.'

MESSAGE_FOR_BACK_TO_PRODUCTS: str = 'Вы вернулись к списку продуктов и услуг: '

MESSAGE_FOR_VIEW_PORTFOLIO: str = (
    'Вот ссылка на наше портфолио [url]. '
    'Хотите узнать больше о конкретны проектах или услугах? '
)

MESSAGE_FOR_COMPANY_INFO: str = (
    'Вот несколько вариантов информации о нашей компании.'
    'Что именно вас интересует?'
)

MESSAGE_FOR_GET_SUPPORT: str = 'Какой вид технической поддержки вам нужен?'

MESSAGE_FOR_PRODUCTS_SERVICES: str = (
    'Мы предлагаем следующие продукты и услуги. '
    'Какой из них вас интересует?'
)


class Form(StatesGroup):
    """Форма для связи с менеджером."""

    first_name = State()
    phone_number = State()


QUESTIONS: dict[Form, str] = {
    Form.first_name: 'Введите ваше имя:',
    Form.phone_number: (
        'Введите ваш номер телефона (в формате +7XXXXXXXXXX '
        'или 8XXXXXXXXXX):'
    )
}


def succses_answer(user_data: dict) -> str:
    return (
        f'Спасибо! Наш менеджер свяжется '
        f'с вами в ближайшее время.\n'
        f'Отправленная форма:\n'
        f'Имя: {user_data['first_name']}\n'
        f'Номер телефона: {user_data['phone_number']}'
    )


INPUT_NUMBER_PHONE: str = (
    'Номер телефона должен быть в формате +7XXXXXXXXXX '
    'или 8XXXXXXXXXX. Попробуйте снова.'
)

INPUT_NAME: str = (
    'Имя должно содержать только буквы. Попробуйте снова.'
)

START_INPUT_USER_DATA: str = (
    'Пожалуйста, оставьте ваше имя и контактный номер, '
    'и наш менеджер свяжется с вами.'
)
