from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройка проекта.

    Взятие данных из .env и их валидация.
    """

    database_url: str
    bot_token: str
    telegram_chat_ids: str
    # email: str
    # email_password: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    db_port: str

    class Config:
        env_file = ".env"


settings = Settings()
