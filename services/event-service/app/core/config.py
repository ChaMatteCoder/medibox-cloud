from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "event-service"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    rabbitmq_url: str
    notification_queue: str = "medibox.notifications"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
