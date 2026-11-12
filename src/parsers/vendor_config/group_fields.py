"""Примитивы структурной проверки настроек товарных групп."""

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.fields import read_text
from parsers.vendor_config.group_validation import validate_reading_settings

READING_KEYS = ('start_row', 'file_templates')
type GroupObjects = tuple[RawConfig, ...]


def reading_defaults(payload: RawConfig, where: str) -> RawConfig:
    """Общие значения нового формата ограничены механикой чтения."""
    defaults = read_object(payload, 'defaults', where)
    for key in defaults:
        if key not in READING_KEYS:
            raise ConfigValidationError(
                f'{where} → defaults → {key}: допустимы только настройки чтения; '
                'перенесите настройки модели в product_groups[].defaults'
            )
    validate_reading_settings(defaults, f'{where} → defaults')
    return defaults


def read_group_id(payload: RawConfig, where: str) -> ProductGroup:
    """Идентификатор из закрытого набора без нормализации регистра и пробелов."""
    identifier = read_text(payload, 'id', f'{where}.id')
    try:
        return ProductGroup(identifier)
    except ValueError as error:
        allowed = ', '.join(ProductGroup)
        raise ConfigValidationError(f'{where}.id: неизвестная группа {identifier!r}; допустимы {allowed}') from error


def object_list(raw: object, where: str) -> GroupObjects:
    """Обязательный непустой список объектов с адресом каждого элемента."""
    if not isinstance(raw, list) or not raw:
        raise ConfigValidationError(f'{where}: требуется непустой список')
    entries = []
    for index, entry in enumerate(raw):
        entries.append(as_config_object(entry, f'{where}[{index}]'))
    return tuple(entries)
