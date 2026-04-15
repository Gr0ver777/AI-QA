"""Конфигурация проекта."""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Настройки приложения."""

    # Playwright settings
    BASE_URL: str = Field(default="http://localhost:3000", description="Базовый URL приложения")
    HEADLESS: bool = Field(default=True, description="Запуск браузера в безголовом режиме")
    SLOW_MO: int = Field(default=0, description="Замедление действий в мс")
    TIMEOUT: int = Field(default=30000, description="Таймаут операций в мс")

    # Database settings
    DB_HOST: str = Field(default="localhost", description="Хост базы данных")
    DB_PORT: int = Field(default=5432, description="Порт базы данных")
    DB_NAME: str = Field(default="test_db", description="Имя базы данных")
    DB_USER: str = Field(default="postgres", description="Пользователь базы данных")
    DB_PASSWORD: str = Field(default="postgres", description="Пароль базы данных")

    # API settings
    API_BASE_URL: str = Field(default="http://localhost:8000/api", description="Базовый URL API")
    API_TIMEOUT: int = Field(default=30, description="Таймаут API запросов в секундах")

    # AI settings
    OPENAI_API_KEY: str = Field(default="", description="API ключ OpenAI")
    OPENAI_MODEL: str = Field(default="gpt-4", description="Модель OpenAI")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
