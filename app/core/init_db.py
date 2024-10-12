from core.db import AsyncSessionLocal
from crud.about_crud import company_info_crud
from app.admin.admin_settings import PORTFOLIO_DEFAULT_DATA


async def add_portfolio():
    """Добавить ссылку на портфолио при запуске бота."""
    async with AsyncSessionLocal() as async_session:
        if not await company_info_crud.get_by_about_name(
            PORTFOLIO_DEFAULT_DATA.get("name"), async_session
        ):
            await company_info_crud.create(
                PORTFOLIO_DEFAULT_DATA, async_session
            )
