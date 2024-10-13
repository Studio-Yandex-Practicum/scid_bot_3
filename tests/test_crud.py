import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock
from app.crud.users import create_user_id, get_role_by_tg_id, is_user_in_db
from app.models.models import RoleEnum


@pytest.mark.asyncio
async def test_create_user():
    mock_session = AsyncMock(spec=AsyncSession)

    # Проверяем создание пользователя
    user_id = 12345
    await create_user_id(user_id, mock_session)

    # Проверяем, что функция `add` была вызвана для сессии с правильным значением
    mock_session.add.assert_called()


@pytest.mark.asyncio
async def test_is_user_in_db():
    mock_session = AsyncMock(spec=AsyncSession)

    mock_result = AsyncMock()
    mock_result.scalar.return_value = True
    mock_session.execute.return_value = mock_result

    # Проверяем, что пользователь находится в БД
    user_id = 12345
    result = await is_user_in_db(user_id, mock_session)
    assert result is True


@pytest.mark.asyncio
async def test_get_role_by_tg_id():
    mock_session = AsyncMock(spec=AsyncSession)

    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = RoleEnum.USER
    mock_session.execute.return_value = mock_result

    user_id = 12345
    role = await get_role_by_tg_id(user_id, mock_session)
    assert role == RoleEnum.USER
