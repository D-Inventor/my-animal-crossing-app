from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    connectionstring: str = Field(..., alias="DATABASE_CONNECTIONSTRING")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
