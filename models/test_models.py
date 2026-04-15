"""Модели данных для тест-кейсов."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TestStep(BaseModel):
    """Шаг тест-кейса."""

    step_number: int = Field(..., description="Номер шага")
    action: str = Field(..., description="Действие")
    expected_result: str = Field(..., description="Ожидаемый результат")
    data: Optional[str] = Field(None, description="Тестовые данные")


class TestCase(BaseModel):
    """Тест-кейс."""

    id: str = Field(..., description="Уникальный идентификатор тест-кейса")
    title: str = Field(..., description="Название тест-кейса")
    description: str = Field(..., description="Описание тест-кейса")
    precondition: Optional[str] = Field(None, description="Предусловия")
    steps: List[TestStep] = Field(..., description="Шаги тестирования")
    postcondition: Optional[str] = Field(None, description="Постусловия")
    priority: str = Field(default="medium", description="Приоритет (high, medium, low)")
    tags: Optional[List[str]] = Field(None, description="Теги")


class BusinessRequirement(BaseModel):
    """Бизнес-требование."""

    id: str = Field(..., description="Уникальный идентификатор требования")
    title: str = Field(..., description="Название требования")
    description: str = Field(..., description="Описание требования")
    acceptance_criteria: List[str] = Field(..., description="Критерии приемки")


class TestSuite(BaseModel):
    """Набор тест-кейсов."""

    name: str = Field(..., description="Название набора тестов")
    description: Optional[str] = Field(None, description="Описание набора")
    test_cases: List[TestCase] = Field(..., description="Список тест-кейсов")
