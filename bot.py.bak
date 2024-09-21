import os
import sys

from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')


def check_tokens():
    """Проверяет наличие необходимых для работы программы токенов."""
    tokens_bool = True
    for token in (BOT_TOKEN):
        if not token:
            tokens_bool = False
    return tokens_bool


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Отсутствует токен!')


if __name__ == '__main__':
    """Запуск работы бота."""
    main()
