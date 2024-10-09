from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройка проекта.

    Взятие данных из .env и их валидация.
    """
    database_url: str
    bot_token: str
    telegram_chat_ids: str

    class Config:
        env_file = '.env'


settings = Settings()
