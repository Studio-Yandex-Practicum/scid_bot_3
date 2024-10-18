import redis.asyncio as aioredis


async def get_redis_connection():
    """Подключение к Redis."""

    return await aioredis.from_url(
        "redis://localhost:6379", decode_responses=True
    )
