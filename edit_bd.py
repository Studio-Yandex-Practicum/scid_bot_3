import asyncio
import random
import faker
from db.db_base import AsyncSessionLocal

from CRUD.user_crud import user_crud
from CRUD.category_product import category_product_crud
from CRUD.feedback_crud import feedback_crud
from CRUD.info_crud import info_crud
from CRUD.about_crud import company_info_crud
from models import User

fake = faker.Faker("ru_RU")

# Создание списка пользователей
users_dict = []
for _ in range(20):
    user = {
        "telegram_id": random.randint(
            100000000, 999999999
        ),  # Случайный telegram_id
        "name": fake.name(),  # Случайное имя
        "phone": fake.phone_number(),  # Случайный номер телефона
        "callback_request": True,
        "callback_request_date": fake.date_time_this_year(),
    }
    users_dict.append(user)


feedback_dict = []

for _ in range(20):
    feedback = {
        "user": random.randint(1, 20),
        "feedback_text": fake.text(max_nb_chars=100),
        "feedback_date": fake.date_time_this_year(),
    }
    feedback_dict.append(feedback)


# async def get_async_session():
#     async with AsyncSessionLocal() as async_session:
#         await feedback_crud.bulk_create(feedback_dict, async_session)


# async def get_async_session():
#     async with AsyncSessionLocal() as async_session:
#         await user_crud.bulk_create(users_dict, async_session)

async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        info = await company_info_crud.get(1, async_session)
        await company_info_crud.update(info, {"url": "https://skid.ru/cases/"}, async_session)


if __name__ == "__main__":
    asyncio.run(get_async_session())
