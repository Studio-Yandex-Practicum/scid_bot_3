import logging
import asyncio

from bot_setup import bot, dispatcher, check_token
from bot.handlers import router as message_router
from bot.callbacks import router as callback_router
from bot.fsm_context import router as fsm_context_router


async def main() -> None:
    """Запуск SCID бота."""

    try:
        check_token()
    except ValueError as e:
        print(e)
        return

    dispatcher.include_router(message_router)
    dispatcher.include_router(callback_router)
    dispatcher.include_router(fsm_context_router)

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
