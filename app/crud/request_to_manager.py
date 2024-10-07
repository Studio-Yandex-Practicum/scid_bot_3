from datetime import datetime

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
