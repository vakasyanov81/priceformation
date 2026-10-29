"""Настройки дублей из parse_config/doubles.json: в каких шаблонах исключать дубли и чьи позиции важнее."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from domain.exceptions import ConfigValidationError
from domain.protocols import ConfigProvider
from infrastructure.data.file_reader import read_json_file
from parsers.data_provider.json_fields import as_config_object
from parsers.vendor_config.fields import read_str_list

DOUBLES_CONFIG_FILE = 'doubles.json'


@dataclass(frozen=True)
class DoublesSettings:
    """Шаблоны, в которых из группы дублей остаётся одна строка, и приоритетные поставщики."""

    exclude_in_templates: tuple[str, ...] = ()
    priority_suppliers: tuple[str, ...] = ()

    def excludes_in(self, template_name: str) -> bool:
        """Исключать ли дубли в шаблоне с этим именем CLI."""
        return template_name in self.exclude_in_templates


def load_doubles_settings(known_templates: tuple[str, ...], config_provider: ConfigProvider) -> DoublesSettings:
    """Прочитать doubles.json; файла нет — дубли нигде не исключаются."""
    path = config_provider.config_file(DOUBLES_CONFIG_FILE)
    if not Path(path).is_file():
        return DoublesSettings()
    return parse_doubles_settings(read_json_file(path), known_templates)


def parse_doubles_settings(payload: Any, known_templates: tuple[str, ...]) -> DoublesSettings:
    """Проверить структуру doubles.json; неизвестный шаблон — ошибка с путём до ключа."""
    raw = as_config_object(payload, DOUBLES_CONFIG_FILE)
    templates = read_str_list(raw, 'exclude_in_templates', DOUBLES_CONFIG_FILE, default=())
    for index, name in enumerate(templates):
        _ensure_known_template(name, index, known_templates)
    suppliers = read_str_list(raw, 'priority_suppliers', DOUBLES_CONFIG_FILE, default=())
    return DoublesSettings(
        exclude_in_templates=templates,
        priority_suppliers=tuple(supplier.strip() for supplier in suppliers if supplier.strip()),
    )


def _ensure_known_template(name: str, index: int, known_templates: tuple[str, ...]) -> None:
    if name in known_templates:
        return
    available = ', '.join(known_templates)
    raise ConfigValidationError(
        f'{DOUBLES_CONFIG_FILE} → exclude_in_templates[{index}]: шаблон {name!r} не существует. '
        f'Доступны: {available}',
    )
