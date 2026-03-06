from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CRM Jurídico de Cobrança"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./crm_juridico.db"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
