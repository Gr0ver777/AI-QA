"""Агент для генерации тест-кейсов на основе бизнес-требований."""

import json
from typing import List, Optional
from openai import OpenAI
from config import settings
from models import TestCase, TestStep, BusinessRequirement, TestSuite


class TestCaseGeneratorAgent:
    """Агент для генерации тест-кейсов."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def _create_system_prompt(self) -> str:
        """Создание системного промпта."""
        return """Ты опытный QA инженер, специализирующийся на создании тест-кейсов.
Твоя задача - создавать подробные, структурированные тест-кейсы на основе бизнес-требований.

Каждый тест-кейс должен содержать:
- Уникальный ID (например: TC_001)
- Название (краткое и понятное)
- Описание (что тестируем)
- Предусловия (если есть)
- Шаги тестирования (нумерованный список с действием и ожидаемым результатом)
- Постусловия (если есть)
- Приоритет (high, medium, low)
- Теги (опционально)

Формат ответа должен быть JSON массив тест-кейсов."""

    def _create_user_prompt(self, requirements: List[BusinessRequirement]) -> str:
        """Создание пользовательского промпта."""
        prompt = "Создай тест-кейсы на основе следующих бизнес-требований:\n\n"
        
        for req in requirements:
            prompt += f"Требование {req.id}: {req.title}\n"
            prompt += f"Описание: {req.description}\n"
            prompt += "Критерии приемки:\n"
            for i, criterion in enumerate(req.acceptance_criteria, 1):
                prompt += f"  {i}. {criterion}\n"
            prompt += "\n"
        
        prompt += "\nВерни ответ в формате JSON:"
        return prompt

    def generate_test_cases(
        self,
        requirements: List[BusinessRequirement],
        max_tokens: int = 4000,
    ) -> TestSuite:
        """
        Генерация тест-кейсов на основе бизнес-требований.

        Args:
            requirements: Список бизнес-требований
            max_tokens: Максимальное количество токенов в ответе

        Returns:
            TestSuite с набором сгенерированных тест-кейсов
        """
        if not self.client:
            raise ValueError("OpenAI API key не установлен")

        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(requirements)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        
        # Парсим JSON ответ
        try:
            # Пытаемся найти JSON в ответе
            start_idx = content.find("[")
            end_idx = content.rfind("]") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                test_cases_data = json.loads(json_str)
            else:
                test_cases_data = json.loads(content)
            
            # Конвертируем в модели
            test_cases = []
            for tc_data in test_cases_data:
                steps = []
                for step_data in tc_data.get("steps", []):
                    steps.append(TestStep(**step_data))
                
                test_case = TestCase(
                    id=tc_data.get("id", f"TC_{len(test_cases) + 1:03d}"),
                    title=tc_data.get("title", ""),
                    description=tc_data.get("description", ""),
                    precondition=tc_data.get("precondition"),
                    steps=steps,
                    postcondition=tc_data.get("postcondition"),
                    priority=tc_data.get("priority", "medium"),
                    tags=tc_data.get("tags"),
                )
                test_cases.append(test_case)
            
            return TestSuite(
                name=f"Test Suite for {requirements[0].title if requirements else 'Requirements'}",
                description="Сгенерированный набор тест-кейсов",
                test_cases=test_cases,
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON ответа: {e}")

    def generate_from_text(self, requirement_text: str) -> TestSuite:
        """
        Генерация тест-кейсов из текстового описания требования.

        Args:
            requirement_text: Текстовое описание бизнес-требования

        Returns:
            TestSuite с набором сгенерированных тест-кейсов
        """
        requirement = BusinessRequirement(
            id="REQ_001",
            title="Текстовое требование",
            description=requirement_text,
            acceptance_criteria=["Соответствие описанию"],
        )
        return self.generate_test_cases([requirement])

    def export_to_file(self, test_suite: TestSuite, filepath: str, format: str = "json"):
        """
        Экспорт тест-кейсов в файл.

        Args:
            test_suite: Набор тест-кейсов
            filepath: Путь к файлу
            format: Формат экспорта (json, md)
        """
        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(test_suite.dict(), f, indent=2, ensure_ascii=False)
        elif format == "md":
            self._export_to_markdown(test_suite, filepath)

    def _export_to_markdown(self, test_suite: TestSuite, filepath: str):
        """Экспорт в Markdown формат."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {test_suite.name}\n\n")
            if test_suite.description:
                f.write(f"{test_suite.description}\n\n")
            
            for tc in test_suite.test_cases:
                f.write(f"## {tc.id}: {tc.title}\n\n")
                f.write(f"**Описание:** {tc.description}\n\n")
                
                if tc.precondition:
                    f.write(f"**Предусловия:** {tc.precondition}\n\n")
                
                f.write("**Шаги тестирования:**\n\n")
                f.write("| № | Действие | Ожидаемый результат | Данные |\n")
                f.write("|---|----------|---------------------|--------|\n")
                
                for step in tc.steps:
                    data = step.data or "-"
                    f.write(f"| {step.step_number} | {step.action} | {step.expected_result} | {data} |\n")
                
                f.write("\n")
                
                if tc.postcondition:
                    f.write(f"**Постусловия:** {tc.postcondition}\n\n")
                
                f.write(f"**Приоритет:** {tc.priority}\n\n")
                if tc.tags:
                    f.write(f"**Теги:** {', '.join(tc.tags)}\n\n")
                
                f.write("---\n\n")
