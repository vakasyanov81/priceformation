"""ConfigProvider по файловой структуре проекта."""

from pathlib import Path

from domain.protocols import ConfigProvider

_PARSE_CONFIG_FOLDER = 'parse_config'
_PRICES_FOLDER = 'file_prices'
_RESULT_FOLDER = 'result'
_LOGS_FOLDER = 'logs'
_ROOT_PARENTS_COUNT = 3  # config -> infrastructure -> src -> корень проекта


class FileConfigProvider(ConfigProvider):
    """Пути окружения из структуры репозитория: parse_config, file_prices, logs."""

    def __init__(self, project_root: str | None = None) -> None:
        """init"""
        self._root = project_root or _detect_project_root()
        self._user_config = str(Path(self._root) / _PARSE_CONFIG_FOLDER)
        self._prices = str(Path(self._root) / _PRICES_FOLDER)
        self._output = str(Path(self._prices) / _RESULT_FOLDER)
        self._logs = str(Path(self._root) / _LOGS_FOLDER)

    @property
    def project_root(self) -> str:
        """Корень проекта."""
        return self._root

    def config_file(self, name: str) -> str:
        """Полный путь к файлу настроек в parse_config."""
        return str(Path(self._user_config) / name)

    def price_folder(self, supplier_folder: str) -> str:
        """Путь к папке прайсов поставщика."""
        return str(Path(self._prices) / supplier_folder)

    def result_folder(self) -> str:
        """Папка для записанных результатов."""
        return self._output

    def log_folder(self) -> str:
        """Папка для файлов логов."""
        return self._logs


def _detect_project_root() -> str:
    """Корень проекта: уровнем выше папки пакета src."""
    return str(Path(__file__).resolve().parents[_ROOT_PARENTS_COUNT])
