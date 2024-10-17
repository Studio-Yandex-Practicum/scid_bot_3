from admin.admin_settings import PORTFOLIO_DEFAULT_DATA
from admin.admin_settings import admin_list
from crud.users import create_user_id
from crud.user_crud import user_crud
from core.db import AsyncSessionLocal
from crud.portfolio_projects_crud import portfolio_crud


async def add_portfolio():
    """Добавить ссылку на портфолио при запуске бота."""

    async with AsyncSessionLocal() as async_session:
        if not await portfolio_crud.get_by_string(
            PORTFOLIO_DEFAULT_DATA.get("name"), async_session
        ):
            await portfolio_crud.create(PORTFOLIO_DEFAULT_DATA, async_session)


async def set_admin():
    """Добавить все TELEGRAM_IDS в администраторы."""
    async with AsyncSessionLocal() as session:
        for admin in admin_list:
            if not await user_crud.get_user_by_tg_id(admin, session):
                user = await create_user_id(admin, session)
                await user_crud.update(user, {"role": "ADMIN"}, session)
