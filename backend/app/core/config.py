from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "APIlytics Backend"
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://apilytics:apilytics@localhost:5432/apilytics"
    
    # Cost Estimator (Demo)
    COST_PER_1000_REQUESTS: float = 1.0
    COST_UNIT: str = "demo-units"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Load from .env file if it exists (ignores extra vars)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Create a global settings instance
settings = Settings()
