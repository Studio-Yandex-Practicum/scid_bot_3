from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    declarative_base, declared_attr, sessionmaker, Mapped, mapped_column
)

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./dev.db'
    bot_token: str

    class Config:
        env_file = '.env'


settings = Settings()


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)
engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
