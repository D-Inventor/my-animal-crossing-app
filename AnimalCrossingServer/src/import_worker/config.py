from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NookipediaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NOOKIPEDIA_")

    base_url: str = Field()
