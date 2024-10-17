import pytest
from aiogram.types import Message


@pytest.fixture
def fake_message():
    return Message(chat={'id': 123}, text='/start')
