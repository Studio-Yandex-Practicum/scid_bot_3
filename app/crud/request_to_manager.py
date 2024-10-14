from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import ContactManager


async def create_request_to_manager(
    user_data: dict, request_type: str, session: AsyncSession
) -> ContactManager:
    """Создание заявки на связь с менеджером."""

    data_to_db = ContactManager(
        **user_data,
        shipping_date=datetime.utcnow(),
        need_support=(request_type == 'callback_request'),
        need_contact_with_manager=(request_type == 'contact_manager')
    )

    session.add(data_to_db)
    await session.commit()
    await session.refresh(data_to_db)

    return data_to_db


async def get_request(request_id: int, session: AsyncSession):
    """Получить запрос по id."""
    request = await session.execute(
        select(ContactManager).where(ContactManager.id == request_id)
    )
    return request.scalars().first()


async def get_all_support_requests(session: AsyncSession):
    """Получить список активных заявок на поддержку."""
    support_requests = await session.execute(
        select(ContactManager).where(
            and_(
                ContactManager.shipping_date_close.is_(None),
                ContactManager.need_support.is_(True),
            )
        )
    )
    return support_requests.scalars().all()


async def get_all_manager_requests(session: AsyncSession):
    """Получить список активных заявок на звонок менеджера."""
    support_requests = await session.execute(
        select(ContactManager).where(
            and_(
                ContactManager.shipping_date_close.is_(None),
                ContactManager.need_contact_with_manager.is_(True),
            )
        )
    )
    return support_requests.scalars().all()


async def close_case(request_id: int, session: AsyncSession):
    """Закрыть заявку."""
    case_to_close = await get_request(request_id, session)
    if case_to_close.need_contact_with_manager:
        setattr(case_to_close, "need_contact_with_manager", False)
    elif case_to_close.need_support:
        setattr(case_to_close, "need_support", False)
    setattr(case_to_close, "shipping_date_close", datetime.now())
    session.add(case_to_close)
    await session.commit()
    await session.refresh(case_to_close)
    return case_to_close
