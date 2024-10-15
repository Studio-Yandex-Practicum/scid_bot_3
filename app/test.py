import asyncio
from datetime import datetime

from core.db import AsyncSessionLocal
from crud.feedback_crud import feedback_crud



feedbacks = {
    "user": 1,
    "feedback_text": "Типа отзыв",
    "feedback_date": datetime.now(),
    "rating": 5

}

async def add_to_db():
    async with AsyncSessionLocal() as session:
        await feedback_crud.create(feedbacks, session)


if __name__ == "__main__":
    asyncio.run(add_to_db())