import logging

from loggers.log import setup_logging
from redis_db.connect import get_redis_connection

setup_logging()
logger = logging.getLogger(__name__)


async def set_user_timeout(user_id: int, timeout: int):
    """Устанавливает таймаут для пользователя в Redis."""

    redis_client = await get_redis_connection()

    await redis_client.set("timeout", timeout)
    await redis_client.close()

    logger.info(
        f"Таймаут для пользователя {user_id} установлен на {timeout} секунд."
    )
