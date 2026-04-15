"""Модуль страниц."""

from .base_page import BasePage
from .elements import (
    BaseElement,
    Button,
    Input,
    Checkbox,
    Dropdown,
    Table,
    Modal,
)
from .factories import PageFactory

__all__ = [
    "BasePage",
    "BaseElement",
    "Button",
    "Input",
    "Checkbox",
    "Dropdown",
    "Table",
    "Modal",
    "PageFactory",
]
