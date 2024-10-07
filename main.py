import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.admin_handlers import admin_router
from handlers.user import user_router
from middlewares.session_middleware import DataBaseSession
from db.init_db import add_portfolio
from db.db_base import AsyncSessionLocal


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)

dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_router)


async def main():
    dp.update.middleware(DataBaseSession(session_pool=AsyncSessionLocal))
    await add_portfolio()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
