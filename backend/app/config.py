from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://app:app@db:5432/app"
    cors_origins: list[str] = ["http://localhost:3000"]
    data_dir: str = "/data"


settings = Settings()
