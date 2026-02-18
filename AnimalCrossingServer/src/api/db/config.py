from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = Field()
    port: int = Field(3306)

    username: str = Field()
    password: str | None = Field(None)
    password_file: str | None = Field(None)

    database: str = Field()

    def get_password(self) -> str:
        if self.password is not None:
            return self.password

        if self.password_file is not None:
            return self.get_password_from_file()

        raise ValueError("Neither password, nor password_file is configured.")

    def get_password_from_file(self) -> str:
        with open(self.password_file) as f:
            return f.readline().rstrip("\n")

    def get_connection_url(self) -> URL:
        return URL.create(
            drivername="mysql+pymysql",
            username=self.username,
            password=self.get_password(),
            host=self.host,
            port=self.port,
            database=self.database,
        )
