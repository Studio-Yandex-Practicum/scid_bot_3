import os
import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import router


load_dotenv()


bot = Bot(token=os.getenv('BOT_TOKEN'))
dispatcher = Dispatcher()


async def main() -> None:
    """Запуск SCID бота."""

    if os.getenv('BOT_TOKEN') is None:  # нарушает solid - принцип ед. наследсвенности
        sys.exit('Отсутсвуют необходимые токены.')

    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
