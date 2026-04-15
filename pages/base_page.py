"""Базовая страница."""

from typing import Optional
from playwright.sync_api import Page, expect
from config import settings


class BasePage:
    """Базовый класс для всех страниц."""

    def __init__(self, page: Page):
        self.page = page
        self.factory = None  # Будет инициализирована в подклассах

    @property
    def url(self) -> str:
        """Получение URL страницы."""
        return f"{settings.BASE_URL}/"

    def open(self):
        """Открытие страницы."""
        self.page.goto(self.url)
        return self

    def open_relative(self, path: str):
        """Открытие относительного пути."""
        self.page.goto(f"{settings.BASE_URL}{path}")
        return self

    @property
    def title(self) -> str:
        """Получение заголовка страницы."""
        return self.page.title()

    def wait_for_title(self, expected_title: str, timeout: Optional[int] = None):
        """Ожидание заголовка страницы."""
        kwargs = {}
        if timeout:
            kwargs["timeout"] = timeout
        expect(self.page).to_have_title(expected_title, **kwargs)
        return self

    def wait_for_url(self, expected_url: str, timeout: Optional[int] = None):
        """Ожидание URL страницы."""
        kwargs = {}
        if timeout:
            kwargs["timeout"] = timeout
        expect(self.page).to_have_url(expected_url, **kwargs)
        return self

    def screenshot(self, path: Optional[str] = None):
        """Скриншот страницы."""
        if path:
            self.page.screenshot(path=path)
        else:
            self.page.screenshot(path=f"screenshots/{self.__class__.__name__}.png")
        return self

    def refresh(self):
        """Обновление страницы."""
        self.page.reload()
        return self

    def go_back(self):
        """Назад в истории браузера."""
        self.page.go_back()
        return self

    def go_forward(self):
        """Вперед в истории браузера."""
        self.page.go_forward()
        return self

    @property
    def current_url(self) -> str:
        """Получение текущего URL."""
        return self.page.url

    def wait_for_load_state(self, state: str = "load", timeout: Optional[int] = None):
        """Ожидание состояния загрузки."""
        kwargs = {}
        if timeout:
            kwargs["timeout"] = timeout
        self.page.wait_for_load_state(state, **kwargs)
        return self

    def evaluate(self, script: str):
        """Выполнение JavaScript кода."""
        return self.page.evaluate(script)
