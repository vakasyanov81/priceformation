"""Порты домена: контракты, которые реализует инфраструктура."""

from typing import Protocol


class ConfigProvider(Protocol):
    """Провайдер путей окружения: настройки, прайсы, результаты и логи."""

    @property
    def project_root(self) -> str:
        """Корень проекта."""
        ...

    def config_file(self, name: str) -> str:
        """Полный путь к файлу настроек в parse_config."""
        ...

    def price_folder(self, supplier_folder: str) -> str:
        """Путь к папке прайсов поставщика."""
        ...

    def result_folder(self) -> str:
        """Папка для записанных результатов."""
        ...

    def log_folder(self) -> str:
        """Папка для файлов логов."""
        ...
