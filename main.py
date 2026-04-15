"""Пример использования агентов для генерации тест-кейсов и автотестов."""

from agents import TestCaseGeneratorAgent, AutoTestGeneratorAgent
from models import BusinessRequirement
from utils import setup_logging


def main():
    """Основная функция демонстрации работы агентов."""
    # Настройка логирования
    logger = setup_logging("INFO")
    logger.info("Запуск демонстрации AI-QA агентов")
    
    # Пример бизнес-требования
    requirement = BusinessRequirement(
        id="REQ_001",
        title="Авторизация пользователя",
        description="""
        Система должна предоставлять возможность пользователям авторизоваться.
        Пользователь должен ввести email и пароль.
        После успешной авторизации пользователь перенаправляется на главную страницу.
        При неудачной авторизации отображается сообщение об ошибке.
        """,
        acceptance_criteria=[
            "Пользователь может ввести email в поле ввода",
            "Пользователь может ввести пароль в поле ввода",
            "При вводе корректных данных происходит авторизация",
            "При вводе некорректных данных отображается ошибка",
            "Кнопка 'Войти' активна только при заполненных полях",
        ]
    )
    
    # Инициализация агента генерации тест-кейсов
    # Примечание: Для работы требуется OPENAI_API_KEY в .env файле
    try:
        tc_generator = TestCaseGeneratorAgent()
        
        logger.info("Генерация тест-кейсов на основе бизнес-требований...")
        test_suite = tc_generator.generate_test_cases([requirement])
        
        logger.info(f"Сгенерировано {len(test_suite.test_cases)} тест-кейсов")
        
        # Экспорт тест-кейсов в файл
        tc_generator.export_to_file(test_suite, "test_cases.json", format="json")
        tc_generator.export_to_file(test_suite, "test_cases.md", format="md")
        logger.info("Тест-кейсы экспортированы в test_cases.json и test_cases.md")
        
    except ValueError as e:
        logger.warning(f"Не удалось сгенерировать тест-кейсы: {e}")
        logger.info("Создадим демо тест-кейс вручную для демонстрации")
        
        from models import TestCase, TestStep
        test_suite = None
    
    # Если генерация через AI не удалась, создадим демо тест-кейс
    if not test_suite or len(test_suite.test_cases) == 0:
        test_suite = type('TestSuite', (), {
            'name': 'Demo Test Suite',
            'test_cases': [
                TestCase(
                    id="TC_001",
                    title="Успешная авторизация",
                    description="Проверка успешной авторизации пользователя",
                    precondition="Пользователь зарегистрирован",
                    steps=[
                        TestStep(step_number=1, action="Открыть страницу авторизации", expected_result="Страница загружена"),
                        TestStep(step_number=2, action="Ввести корректный email", expected_result="Email введен", data="user@example.com"),
                        TestStep(step_number=3, action="Ввести корректный пароль", expected_result="Пароль введен", data="password123"),
                        TestStep(step_number=4, action="Нажать кнопку 'Войти'", expected_result="Происходит авторизация и перенаправление"),
                    ],
                    priority="high",
                    tags=["auth", "smoke"]
                ),
                TestCase(
                    id="TC_002",
                    title="Неуспешная авторизация",
                    description="Проверка авторизации с неверными данными",
                    precondition="Пользователь зарегистрирован",
                    steps=[
                        TestStep(step_number=1, action="Открыть страницу авторизации", expected_result="Страница загружена"),
                        TestStep(step_number=2, action="Ввести некорректный email", expected_result="Email введен", data="invalid@example.com"),
                        TestStep(step_number=3, action="Ввести неверный пароль", expected_result="Пароль введен", data="wrongpassword"),
                        TestStep(step_number=4, action="Нажать кнопку 'Войти'", expected_result="Отображается сообщение об ошибке"),
                    ],
                    priority="medium",
                    tags=["auth", "negative"]
                )
            ]
        })()
    
    # Инициализация агента генерации автотестов
    at_generator = AutoTestGeneratorAgent(output_dir="tests")
    
    logger.info("Генерация автотестов на основе тест-кейсов...")
    
    # Генерация conftest.py
    conftest_path = at_generator.generate_conftest()
    logger.info(f"Создан файл конфигурации pytest: {conftest_path}")
    
    # Генерация тестов для каждого тест-кейса
    for test_case in test_suite.test_cases:
        test_file = at_generator.generate_test_file(test_case)
        logger.info(f"Создан автотест: {test_file}")
        
        # Также можно сгенерировать API и DB тесты
        # api_test_file = at_generator.generate_api_test(test_case, "/api/auth/login")
        # logger.info(f"Создан API тест: {api_test_file}")
        # 
        # db_test_file = at_generator.generate_db_test(test_case, "users")
        # logger.info(f"Создан DB тест: {db_test_file}")
    
    logger.info("Генерация автотестов завершена!")
    logger.info("=" * 60)
    logger.info("Структура проекта:")
    logger.info("""
    /workspace
    ├── agents/           # Агенты для генерации тестов
    ├── api/              # API клиент
    ├── config/           # Конфигурация
    ├── database/         # Работа с БД
    ├── models/           # Модели данных
    ├── pages/            # Page Objects
    │   ├── elements/     # Элементы страницы
    │   └── factories/    # Page Factory
    ├── tests/            # Сгенерированные тесты
    ├── utils/            # Утилиты
    └── requirements.txt  # Зависимости
    """)
    logger.info("=" * 60)
    logger.info("Для запуска тестов выполните:")
    logger.info("  pip install -r requirements.txt")
    logger.info("  playwright install")
    logger.info("  pytest tests/")


if __name__ == "__main__":
    main()
