import datetime
import pytest
from unittest.mock import AsyncMock
from aiogram import Bot
from aiogram.types import Chat, Message, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.handlers import cmd_start
from app.bot.keyborads import main_keyboard
from app.bot.bot_const import START_MESSAGE


@pytest.mark.asyncio
async def test_cmd_start():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = AsyncMock().return_value

    # Создаем мок-объект для бота
    mock_bot = AsyncMock(spec=Bot)

    chat = Chat(id=123, type='private')

    # Создаем фейковый объект User с ID и именем пользователя
    user = User(id=456, is_bot=False, first_name="TestUser")

    # Создаем фейковое сообщение с обязательными полями
    message = Message(
        message_id=1,  # уникальный идентификатор сообщения
        date=datetime.datetime.now(),  # время отправки сообщения
        chat=chat,  # чат, в который было отправлено сообщение
        from_user=user,  # пользователь, отправивший сообщение
        text='/start'  # текст сообщения
    )

    await cmd_start(message, mock_session, mock_bot)

    # Проверяем, что бот вызвал метод send_message
    mock_bot.send_message.assert_called_with(
        chat_id=123,
        text=START_MESSAGE,
        reply_markup=main_keyboard
    )
