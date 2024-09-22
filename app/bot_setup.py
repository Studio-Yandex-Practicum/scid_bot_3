import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dispatcher = Dispatcher(storage=MemoryStorage())


def check_token() -> None:
    if os.getenv('BOT_TOKEN') is None:
        raise ValueError('Отсутствуют необходимые токены.')
