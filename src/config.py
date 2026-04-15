from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = Path(__file__).parent.joinpath("../.env").resolve(True)
        ignore_extra = True
        extra = "ignore"

    environs: dict = dict()

    ENVIRONMENT: str

    DEBUG: bool

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    PGDATA: str
    POSTGRESDB_URL: str = ""

    REDIS_HOST: str
    REDIS_PORT: int


settings = Settings()

load_dotenv(settings.Config.env_file)
settings.environs = environ

settings.POSTGRESDB_URL = (
    "postgresql://"
    + f"{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    + f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)