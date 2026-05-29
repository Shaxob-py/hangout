from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    TELEGRAM_BOT_TOKEN: str

    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES: int
    JWT_REFRESH_TOKEN_EXPIRES: int
    JWT_ALGORITHM: str

    ADMIN_PASSWORD: str
    ADMIN_TELEGRAM_ID: int
    ADMIN_PHONE:str

    SECRETE_ADMIN_URL: str

    SESSIONMIDDLEWARE: str




    @property
    def postgres_async_url(self):
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    def postgres_sync_url(self):
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent / ".env")


settings = Config()
