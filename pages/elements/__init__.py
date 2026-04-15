"""Элементы страницы."""

from .base_element import BaseElement


class Button(BaseElement):
    """Кнопка."""

    def __init__(self, page, locator):
        super().__init__(page, locator)


class Input(BaseElement):
    """Поле ввода."""

    def __init__(self, page, locator):
        super().__init__(page, locator)

    def enter(self):
        """Нажатие Enter."""
        self.press("Enter")
        return self


class Checkbox(BaseElement):
    """Чекбокс."""

    def __init__(self, page, locator):
        super().__init__(page, locator)

    def toggle(self):
        """Переключение состояния."""
        if self.is_checked():
            self.uncheck()
        else:
            self.check()
        return self


class Dropdown(BaseElement):
    """Выпадающий список."""

    def __init__(self, page, locator):
        super().__init__(page, locator)

    def select_by_text(self, text: str):
        """Выбор по тексту."""
        self.locator.select_option(label=text)
        return self

    def select_by_value(self, value: str):
        """Выбор по значению."""
        self.locator.select_option(value)
        return self

    def select_by_index(self, index: int):
        """Выбор по индексу."""
        self.locator.select_option(index=index)
        return self

    @property
    def selected_option(self) -> str:
        """Получение выбранной опции."""
        return self.locator.evaluate("el => el.options[el.selectedIndex].text")


class Table(BaseElement):
    """Таблица."""

    def __init__(self, page, locator):
        super().__init__(page, locator)

    def get_row(self, row_index: int):
        """Получение строки таблицы."""
        return self.page.locator(f"{self.locator.selector} tr:nth-child({row_index + 1})")

    def get_cell(self, row_index: int, col_index: int):
        """Получение ячейки таблицы."""
        row = self.get_row(row_index)
        return row.locator(f"td:nth-child({col_index + 1})")

    def get_row_count(self) -> int:
        """Получение количества строк."""
        return self.locator.locator("tr").count()


class Modal(BaseElement):
    """Модальное окно."""

    def __init__(self, page, locator):
        super().__init__(page, locator)

    def close(self):
        """Закрытие модального окна."""
        self.locator.locator(".close, [aria-label='Close']").click()
        return self

    def is_open(self) -> bool:
        """Проверка открытости модального окна."""
        return self.is_visible()
