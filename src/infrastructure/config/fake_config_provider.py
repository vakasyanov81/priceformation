"""ConfigProvider для тестов: пути в изолированной папке, без файлов проекта."""

from pathlib import Path

from domain.protocols import ConfigProvider

_PARSE_CONFIG_FOLDER = 'parse_config'
_PRICES_FOLDER = 'file_prices'
_RESULT_FOLDER = 'result'
_LOGS_FOLDER = 'logs'


class FakeConfigProvider(ConfigProvider):
    """Провайдер, отдающий пути в переданной папке и создающий их при старте."""

    def __init__(
        self,
        root: Path,
        *,
        config_folder: Path | None = None,
        prices_folder: Path | None = None,
        result_folder: Path | None = None,
        log_folder: Path | None = None,
    ) -> None:
        """init"""
        self._root = Path(root)
        self._user_config = config_folder or self._root / _PARSE_CONFIG_FOLDER
        self._prices = prices_folder or self._root / _PRICES_FOLDER
        self._output = result_folder or self._prices / _RESULT_FOLDER
        self._logs = log_folder or self._root / _LOGS_FOLDER
        for folder in (self._user_config, self._output, self._logs):
            folder.mkdir(parents=True, exist_ok=True)

    @property
    def project_root(self) -> str:
        """Корень проекта."""
        return str(self._root)

    def config_file(self, name: str) -> str:
        """Полный путь к файлу настроек в parse_config."""
        return str(self._user_config / name)

    def price_folder(self, supplier_folder: str) -> str:
        """Путь к папке прайсов поставщика."""
        return str(self._prices / supplier_folder)

    def result_folder(self) -> str:
        """Папка для записанных результатов."""
        return str(self._output)

    def log_folder(self) -> str:
        """Папка для файлов логов."""
        return str(self._logs)
