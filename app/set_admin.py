import asyncio

from crud.user_crud import user_crud
from core.db import AsyncSessionLocal


async def set_admin():
    """
    После первого запуска бота и чистой БД добавить себя в список админов.
    Не забыть удалить потом этот файл.
    """
    async with AsyncSessionLocal() as session:
        user = await user_crud.get(1, session)
        await user_crud.update(user, {"role": "ADMIN"}, session)


if __name__ == "__main__":
    asyncio.run(set_admin())
