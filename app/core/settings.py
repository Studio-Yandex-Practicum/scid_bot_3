from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    database_url: str
    bot_token: str
    telegram_token: str
    telegram_chat_ids: str
    email: str
    email_password: str
    postgres_user: str
    postgres_password: str
    postgres_db: str

    model_config = ConfigDict(env_file='.env')


settings = Settings()
