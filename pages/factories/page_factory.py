"""Page Factory для создания элементов страницы."""

from typing import Type, Optional
from playwright.sync_api import Page, Locator
from .base_element import BaseElement


class PageFactory:
    """Фабрика для создания элементов страницы."""

    def __init__(self, page: Page):
        self.page = page

    def create_element(
        self,
        element_class: Type[BaseElement],
        selector: str,
        parent_locator: Optional[Locator] = None
    ) -> BaseElement:
        """
        Создание элемента страницы.

        Args:
            element_class: Класс элемента
            selector: CSS селектор элемента
            parent_locator: Родительский локатор (опционально)

        Returns:
            Экземпляр элемента
        """
        if parent_locator:
            locator = parent_locator.locator(selector)
        else:
            locator = self.page.locator(selector)
        
        return element_class(self.page, locator)

    def create_button(self, selector: str, parent: Optional[Locator] = None):
        """Создание кнопки."""
        from .elements import Button
        return self.create_element(Button, selector, parent)

    def create_input(self, selector: str, parent: Optional[Locator] = None):
        """Создание поля ввода."""
        from .elements import Input
        return self.create_element(Input, selector, parent)

    def create_checkbox(self, selector: str, parent: Optional[Locator] = None):
        """Создание чекбокса."""
        from .elements import Checkbox
        return self.create_element(Checkbox, selector, parent)

    def create_dropdown(self, selector: str, parent: Optional[Locator] = None):
        """Создание выпадающего списка."""
        from .elements import Dropdown
        return self.create_element(Dropdown, selector, parent)

    def create_table(self, selector: str, parent: Optional[Locator] = None):
        """Создание таблицы."""
        from .elements import Table
        return self.create_element(Table, selector, parent)

    def create_modal(self, selector: str, parent: Optional[Locator] = None):
        """Создание модального окна."""
        from .elements import Modal
        return self.create_element(Modal, selector, parent)

    def find_all(self, selector: str) -> list[Locator]:
        """Поиск всех элементов по селектору."""
        return self.page.locator(selector).all()

    def wait_for_element(
        self,
        selector: str,
        state: str = "visible",
        timeout: Optional[int] = None
    ) -> Locator:
        """Ожидание появления элемента."""
        kwargs = {"state": state}
        if timeout:
            kwargs["timeout"] = timeout
        
        locator = self.page.locator(selector)
        locator.wait_for(**kwargs)
        return locator
