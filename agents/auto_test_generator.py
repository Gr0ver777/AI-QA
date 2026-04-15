"""Агент для генерации автотестов на основе тест-кейсов."""

import re
from typing import List, Optional
from pathlib import Path
from config import settings
from models import TestCase, TestSuite


class AutoTestGeneratorAgent:
    """Агент для генерации автотестов на основе тест-кейсов."""

    def __init__(self, output_dir: str = "tests"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_imports(self, page_class_name: str) -> str:
        """Генерация импортов для теста."""
        return f'''"""Автотест сгенерированный на основе тест-кейса."""

import pytest
from playwright.sync_api import Page, expect
from pages import BasePage, PageFactory
from pages.elements import Button, Input, Checkbox, Dropdown, Table
from config import settings
'''

    def _generate_page_object_class(self, test_case: TestCase) -> str:
        """Генерация класса Page Object для теста."""
        class_name = self._sanitize_class_name(test_case.title)
        
        code = f'''

class {class_name}Page(BasePage):
    """Page Object для теста: {test_case.title}."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.factory = PageFactory(page)
        
        # Определите элементы страницы здесь
        # Пример:
        # self.submit_button = self.factory.create_button("#submit")
        # self.username_input = self.factory.create_input("#username")
'''
        # Добавляем методы для шагов теста
        for i, step in enumerate(test_case.steps, 1):
            method_name = f"step_{i}_{self._sanitize_method_name(step.action[:30])}"
            code += f'''
    def {method_name}(self):
        """Шаг {i}: {step.action}"""
        # TODO: Реализуйте действия для этого шага
        # Ожидаемый результат: {step.expected_result}
        pass
'''
        
        return code

    def _generate_test_function(self, test_case: TestCase) -> str:
        """Генерация функции теста."""
        test_name = self._sanitize_test_name(test_case.id)
        class_name = self._sanitize_class_name(test_case.title)
        
        # Генерируем код теста на основе шагов
        test_steps_code = ""
        for i, step in enumerate(test_case.steps, 1):
            method_name = f"step_{i}_{self._sanitize_method_name(step.action[:30])}"
            test_steps_code += f"        page_object.{method_name}()\n"
        
        # Добавляем проверки на основе ожидаемых результатов
        assertions_code = ""
        for i, step in enumerate(test_case.steps, 1):
            if "должен" in step.expected_result.lower() or "отображается" in step.expected_result.lower():
                assertions_code += f"        # Проверка шага {i}: {step.expected_result}\n"
                assertions_code += f"        # TODO: Добавьте assertion для проверки\n"
        
        code = f'''

@pytest.mark.parametrize("browser_type", ["chromium"])
def test_{test_name}(page: Page, browser_type: str):
    """
    Тест: {test_case.title}
    
    ID: {test_case.id}
    Описание: {test_case.description}
    Приоритет: {test_case.priority}
    '''
        
        if test_case.precondition:
            code += f'''Предусловия: {test_case.precondition}
    '''
        
        if test_case.postcondition:
            code += f'''Постусловия: {test_case.postcondition}
    '''
        
        code += f'''Теги: {", ".join(test_case.tags) if test_case.tags else "none"}
    """
    # Инициализация страницы
    page.goto(settings.BASE_URL)
    page_object = {class_name}Page(page)
    
    # Выполнение шагов теста
{test_steps_code}
    # Проверки
{assertions_code}
'''
        
        if test_case.priority == "high":
            code = "@pytest.mark.high_priority\n" + code
        
        if test_case.tags:
            for tag in test_case.tags:
                code = f'@pytest.mark.{self._sanitize_tag(tag)}\n' + code
        
        return code

    def _sanitize_class_name(self, name: str) -> str:
        """Очистка имени для названия класса."""
        # Удаляем специальные символы и оставляем буквы и цифры
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        # Преобразуем в PascalCase
        words = sanitized.split()
        return ''.join(word.capitalize() for word in words) or "TestPage"

    def _sanitize_method_name(self, name: str) -> str:
        """Очистка имени для названия метода."""
        # Удаляем специальные символы
        sanitized = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', name)
        # Преобразуем в snake_case
        sanitized = sanitized.lower().replace(' ', '_')
        # Удаляем множественные подчеркивания
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_') or "action"

    def _sanitize_test_name(self, test_id: str) -> str:
        """Очистка ID для названия теста."""
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', test_id)
        return sanitized.lower() or "test_case"

    def _sanitize_tag(self, tag: str) -> str:
        """Очистка тега для маркера pytest."""
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', tag)
        return sanitized.lower() or "tag"

    def generate_test_file(self, test_case: TestCase) -> str:
        """
        Генерация файла с автотестом.

        Args:
            test_case: Тест-кейс для генерации теста

        Returns:
            Путь к созданному файлу
        """
        filename = f"test_{self._sanitize_test_name(test_case.id)}.py"
        filepath = self.output_dir / filename
        
        content = self._generate_imports(self._sanitize_class_name(test_case.title))
        content += self._generate_page_object_class(test_case)
        content += self._generate_test_function(test_case)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)

    def generate_test_suite(self, test_suite: TestSuite) -> List[str]:
        """
        Генерация файлов автотестов для набора тест-кейсов.

        Args:
            test_suite: Набор тест-кейсов

        Returns:
            Список путей к созданным файлам
        """
        filepaths = []
        for test_case in test_suite.test_cases:
            filepath = self.generate_test_file(test_case)
            filepaths.append(filepath)
        return filepaths

    def generate_conftest(self) -> str:
        """Генерация файла conftest.py для pytest."""
        content = '''"""Конфигурация pytest для автотестов."""

import pytest
from playwright.sync_api import sync_playwright
from config import settings


@pytest.fixture(scope="session")
def browser():
    """Фикстура для запуска браузера."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=settings.HEADLESS,
            slow_mo=settings.SLOW_MO
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Фикстура для создания новой страницы."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        base_url=settings.BASE_URL,
    )
    page = context.new_page()
    page.set_default_timeout(settings.TIMEOUT)
    yield page
    context.close()


@pytest.fixture(scope="function")
def auth_token():
    """Фикстура для токена авторизации."""
    # TODO: Реализуйте получение токена авторизации
    return None
'''
        filepath = self.output_dir / "conftest.py"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)

    def generate_api_test(self, test_case: TestCase, api_endpoint: str) -> str:
        """
        Генерация API теста на основе тест-кейса.

        Args:
            test_case: Тест-кейс
            api_endpoint: API эндпоинт для тестирования

        Returns:
            Путь к созданному файлу
        """
        test_name = self._sanitize_test_name(test_case.id)
        filename = f"test_api_{test_name}.py"
        filepath = self.output_dir / filename
        
        content = f'''"""API тест сгенерированный на основе тест-кейса."""

import pytest
from api import BaseAPIClient
from models import TestCase


@pytest.mark.api
def test_api_{test_name}():
    """
    API Тест: {test_case.title}
    
    ID: {test_case.id}
    Описание: {test_case.description}
    Endpoint: {api_endpoint}
    """
    with BaseAPIClient() as api_client:
        # TODO: Реализуйте API запрос на основе шагов теста
        # response = api_client.get("{api_endpoint}")
        
        # TODO: Добавьте проверки на основе ожидаемых результатов
        # assert response.status_code == 200
        pass
'''
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)

    def generate_db_test(self, test_case: TestCase, table_name: str) -> str:
        """
        Генерация DB теста на основе тест-кейса.

        Args:
            test_case: Тест-кейс
            table_name: Имя таблицы для тестирования

        Returns:
            Путь к созданному файлу
        """
        test_name = self._sanitize_test_name(test_case.id)
        filename = f"test_db_{test_name}.py"
        filepath = self.output_dir / filename
        
        content = f'''"""DB тест сгенерированный на основе тест-кейса."""

import pytest
from database import BaseDatabase
from models import TestCase


@pytest.mark.database
def test_db_{test_name}():
    """
    DB Тест: {test_case.title}
    
    ID: {test_case.id}
    Описание: {test_case.description}
    Таблица: {table_name}
    """
    with BaseDatabase() as db:
        # TODO: Реализуйте проверку данных в БД на основе шагов теста
        # result = db.select(table_name, where="id = %s", where_params=(1,))
        
        # TODO: Добавьте проверки на основе ожидаемых результатов
        # assert len(result) > 0
        pass
'''
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)
