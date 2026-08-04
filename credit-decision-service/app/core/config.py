from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    port: int = 8003

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
