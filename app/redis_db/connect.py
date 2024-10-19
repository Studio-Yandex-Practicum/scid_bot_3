import redis.asyncio as aioredis


async def get_redis_connection():
    """Подключение к Redis."""

    return await aioredis.from_url(
        "redis://158.160.77.163:6379", decode_responses=True  # localhost:
    )
