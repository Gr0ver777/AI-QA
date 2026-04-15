"""Утилиты для проекта."""

import logging
from pathlib import Path
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Настройка логирования."""
    logger = logging.getLogger("ai_qa")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Файловый хендлер
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(log_dir / f"test_{timestamp}.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def create_screenshots_dir():
    """Создание директории для скриншотов."""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    return screenshots_dir


def get_timestamp() -> str:
    """Получение текущей временной метки."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
