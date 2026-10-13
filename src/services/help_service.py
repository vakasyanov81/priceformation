"""Пользовательская документация: README.md из корня проекта."""

from pathlib import Path

from domain.config_context import get_config_provider
from infrastructure.data.file_reader import read_file

_README_NAME = 'README.md'


class HelpService:
    """Отдаёт содержимое README.md для показа на экране."""

    def readme(self) -> str:
        """Текст пользовательской документации из корня проекта."""
        return read_file(str(Path(get_config_provider().project_root) / _README_NAME))
