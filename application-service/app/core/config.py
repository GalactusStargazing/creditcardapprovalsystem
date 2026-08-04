from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    credit_decision_service_url: str
    port: int = 8002

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
