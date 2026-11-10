from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "APIlytics Backend"
    VERSION: str = "0.1.0"

    CREATOR_NAME: str = "Abhay Pratap Singh"
    CREATOR_ROLE: str = "Backend and Integration"
    CREATOR_HANDLE: str = "abhaypratap08"

    DEV_MODE: bool = True

    DATABASE_URL: str = "postgresql+psycopg://apilytics:apilytics@localhost:5432/apilytics"
    COST_PER_1000_REQUESTS: float = 1.0
    COST_UNIT: str = "demo-units"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
