# AI-QA Framework

Фреймворк для автоматизации QA процессов с использованием двух AI-агентов.

## Описание

Проект реализует работу QA с помощью двух агентов:

1. **Агент генерации тест-кейсов** - Генерирует тест-кейсы на основе бизнес-требований с использованием AI (OpenAI GPT)
2. **Агент генерации автотестов** - На основе сгенерированных тест-кейсов пишет автотесты, используя паттерны Page Object, Page Element и Page Factory

## Технологии

- **Playwright** - для тестирования фронтенда
- **PostgreSQL** - для работы с базой данных
- **HTTPX** - для работы с API
- **Pytest** - фреймворк для тестирования
- **Pydantic** - для валидации данных
- **OpenAI API** - для генерации тест-кейсов

## Структура проекта

```
/workspace
├── agents/                    # AI агенты
│   ├── test_case_generator.py # Агент генерации тест-кейсов
│   └── auto_test_generator.py # Агент генерации автотестов
├── api/                       # API клиент
│   └── base_client.py
├── config/                    # Конфигурация
│   └── settings.py
├── database/                  # Работа с БД
│   └── base_database.py
├── models/                    # Модели данных
│   └── test_models.py
├── pages/                     # Page Objects
│   ├── elements/              # Элементы страницы
│   │   ├── base_element.py
│   │   └── __init__.py
│   ├── factories/             # Page Factory
│   │   └── page_factory.py
│   ├── base_page.py
│   └── __init__.py
├── tests/                     # Сгенерированные тесты
├── utils/                     # Утилиты
│   └── helpers.py
├── main.py                    # Пример использования
└── requirements.txt           # Зависимости
```

## Установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка браузеров Playwright
playwright install
```

## Настройка

Создайте файл `.env` в корне проекта:

```env
# Playwright settings
BASE_URL=http://localhost:3000
HEADLESS=true
SLOW_MO=0
TIMEOUT=30000

# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=postgres
DB_PASSWORD=postgres

# API settings
API_BASE_URL=http://localhost:8000/api
API_TIMEOUT=30

# AI settings
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4
```

## Использование

### Генерация тест-кейсов из бизнес-требований

```python
from agents import TestCaseGeneratorAgent
from models import BusinessRequirement

# Создание бизнес-требования
requirement = BusinessRequirement(
    id="REQ_001",
    title="Авторизация пользователя",
    description="Система должна предоставлять возможность пользователям авторизоваться...",
    acceptance_criteria=[
        "Пользователь может ввести email",
        "Пользователь может ввести пароль",
        "При успешной авторизации происходит перенаправление",
    ]
)

# Генерация тест-кейсов
generator = TestCaseGeneratorAgent()
test_suite = generator.generate_test_cases([requirement])

# Экспорт в файл
generator.export_to_file(test_suite, "test_cases.md", format="md")
```

### Генерация автотестов на основе тест-кейсов

```python
from agents import AutoTestGeneratorAgent

# Генерация автотестов
auto_generator = AutoTestGeneratorAgent(output_dir="tests")

# Создание conftest.py
auto_generator.generate_conftest()

# Генерация тестов для каждого тест-кейса
for test_case in test_suite.test_cases:
    auto_generator.generate_test_file(test_case)
    
    # Опционально: генерация API тестов
    auto_generator.generate_api_test(test_case, "/api/auth/login")
    
    # Опционально: генерация DB тестов
    auto_generator.generate_db_test(test_case, "users")
```

### Запуск тестов

```bash
# Запуск всех тестов
pytest tests/

# Запуск с отчетом Allure
pytest tests/ --alluredir=allure-results
allure serve allure-results

# Запуск конкретных тестов по тегам
pytest tests/ -m "auth"
pytest tests/ -m "smoke"
```

## Паттерны

### Page Object

Каждая страница приложения представлена классом, который инкапсулирует элементы и действия:

```python
from pages import BasePage, PageFactory
from pages.elements import Button, Input

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.factory = PageFactory(page)
        self.email_input = self.factory.create_input("#email")
        self.password_input = self.factory.create_input("#password")
        self.submit_button = self.factory.create_button("#submit")
    
    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
```

### Page Element

Базовый класс для элементов страницы с общими методами:

```python
from pages.elements import BaseElement

class CustomElement(BaseElement):
    def custom_action(self):
        # Кастомное действие
        pass
```

### Page Factory

Фабрика для создания элементов страницы:

```python
factory = PageFactory(page)
button = factory.create_button("#submit")
input_field = factory.create_input("#username")
```

## Работа с API

```python
from api import BaseAPIClient

with BaseAPIClient() as api:
    response = api.get("/users")
    assert response.status_code == 200
    
    # С авторизацией
    api.set_auth_token("your_token")
    response = api.post("/users", data={"name": "John"})
```

## Работа с базой данных

```python
from database import BaseDatabase

with BaseDatabase() as db:
    # Выборка данных
    users = db.select("users", where="active = %s", where_params=(True,))
    
    # Вставка записи
    user_id = db.insert("users", {"name": "John", "email": "john@example.com"})
    
    # Обновление
    db.update("users", {"active": False}, where="id = %s", where_params=(user_id,))
```

## Пример запуска

```bash
python main.py
```

## Лицензия

MIT
