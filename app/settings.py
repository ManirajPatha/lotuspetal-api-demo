from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HUB_URL: str = "http://localhost:8080"
    DEMO_TENANT_ID: str = "demo"  # your default

settings = Settings()
