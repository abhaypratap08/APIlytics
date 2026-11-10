from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "APIlytics Backend"
    VERSION: str = "0.1.0"

    # Attribution
    CREATOR_NAME: str = "Abhay Pratap Singh"
    CREATOR_ROLE: str = "Backend and Integration"
    CREATOR_HANDLE: str = "abhaypratap08"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://apilytics:apilytics@localhost:5432/apilytics"

    # Cost Estimator (Demo)
    COST_PER_1000_REQUESTS: float = 1.0
    COST_UNIT: str = "demo-units"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
