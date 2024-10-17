from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Timer
from sqlalchemy import select


async def get_timer(session: AsyncSession):
    """Получить значение таймера из БД."""
    timer_from_db = await session.execute(select(Timer).where(Timer.id == 1))
    return timer_from_db.scalar_one_or_none()


async def change_timer(new_timer: int, session: AsyncSession):
    """Установить новое значение таймера."""
    timer = await get_timer(session)
    setattr(timer, "timer", int(new_timer))
    session.add(timer)
    await session.commit()
    await session.refresh(timer)
