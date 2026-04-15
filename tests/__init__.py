"""Конфигурация pytest."""

import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта
sys.path.insert(0, str(Path(__file__).parent.parent))
