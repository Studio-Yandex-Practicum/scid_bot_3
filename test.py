import asyncio

from app.crud.info_crud import info_crud
from app.core.db import AsyncSessionLocal


async def set_admin():
    """
    После первого запуска бота и чистой БД добавить себя в список админов.
    Не забыть удалить потом этот файл.
    """
    async with AsyncSessionLocal() as session:
        info = await info_crud.get(1, session)
        await info_crud.remove(info, session)


if __name__ == "__main__":
    asyncio.run(set_admin())
