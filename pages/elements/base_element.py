"""Базовые элементы страницы."""

from typing import Optional
from playwright.sync_api import Page, Locator


class BaseElement:
    """Базовый класс для элементов страницы."""

    def __init__(self, page: Page, locator: Locator):
        self.page = page
        self.locator = locator

    def click(self, timeout: Optional[int] = None):
        """Клик по элементу."""
        kwargs = {}
        if timeout:
            kwargs["timeout"] = timeout
        self.locator.click(**kwargs)
        return self

    def fill(self, value: str, timeout: Optional[int] = None):
        """Заполнение поля ввода."""
        kwargs = {}
        if timeout:
            kwargs["timeout"] = timeout
        self.locator.fill(value, **kwargs)
        return self

    def type(self, value: str, delay: int = 0):
        """Ввод текста посимвольно."""
        self.locator.type(value, delay=delay)
        return self

    def clear(self):
        """Очистка поля."""
        self.locator.clear()
        return self

    def press(self, key: str):
        """Нажатие клавиши."""
        self.locator.press(key)
        return self

    @property
    def text(self) -> str:
        """Получение текста элемента."""
        return self.locator.text_content() or ""

    @property
    def inner_text(self) -> str:
        """Получение внутреннего текста."""
        return self.locator.inner_text() or ""

    @property
    def input_value(self) -> str:
        """Получение значения поля ввода."""
        return self.locator.input_value() or ""

    def is_visible(self) -> bool:
        """Проверка видимости элемента."""
        return self.locator.is_visible()

    def is_hidden(self) -> bool:
        """Проверка скрытости элемента."""
        return self.locator.is_hidden()

    def is_enabled(self) -> bool:
        """Проверка активности элемента."""
        return self.locator.is_enabled()

    def is_disabled(self) -> bool:
        """Проверка неактивности элемента."""
        return self.locator.is_disabled()

    def wait_for(self, state: str = "visible", timeout: Optional[int] = None):
        """Ожидание состояния элемента."""
        kwargs = {"state": state}
        if timeout:
            kwargs["timeout"] = timeout
        self.locator.wait_for(**kwargs)
        return self

    def hover(self):
        """Наведение курсора на элемент."""
        self.locator.hover()
        return self

    def check(self):
        """Установка чекбокса."""
        self.locator.check()
        return self

    def uncheck(self):
        """Снятие чекбокса."""
        self.locator.uncheck()
        return self

    def is_checked(self) -> bool:
        """Проверка состояния чекбокса."""
        return self.locator.is_checked()

    def select_option(self, value: str):
        """Выбор опции в select."""
        self.locator.select_option(value)
        return self

    def screenshot(self, path: str):
        """Скриншот элемента."""
        self.locator.screenshot(path=path)
        return self

    def get_attribute(self, name: str) -> Optional[str]:
        """Получение атрибута элемента."""
        return self.locator.get_attribute(name)

    def set_input_files(self, files: list | str):
        """Загрузка файлов."""
        self.locator.set_input_files(files)
        return self
