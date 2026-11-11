"""Проверка переносимых имён результата без создания файлов."""

from pathlib import PureWindowsPath
from string import Formatter
from unicodedata import category

from domain.exceptions import ConfigValidationError

MAX_SHEET_NAME = 31
_DEVICE_NAMES = {
    'con',
    'prn',
    'aux',
    'nul',
    *(f'{prefix}{index}' for prefix in ('com', 'lpt') for index in range(1, 10)),
}


def validate_sheet_name(name: str, where: str) -> None:
    """Отклонить имя, которое Excel исправил бы или запретил."""
    invalid = not name.strip() or len(name) > MAX_SHEET_NAME
    invalid = invalid or name.casefold() == 'history'
    invalid = invalid or name.startswith("'") or name.endswith("'")
    if invalid or _forbidden(name, r':\/?*[]'):
        raise ConfigValidationError(f'{where} → sheet_name: недопустимое имя листа {name!r}')


def output_file_name(pattern: str, current_date: str, where: str) -> str:
    """Подставить только дату и проверить имя файла для всех поддерживаемых ОС."""
    _validate_pattern(pattern, where)
    name = pattern.format(now=current_date)
    invalid = not name.endswith('.xlsx') or '..' in name
    invalid = invalid or name.endswith(('.', ' '))
    device = PureWindowsPath(name).stem.split('.')[0].casefold()
    invalid = invalid or device in _DEVICE_NAMES
    if invalid or _forbidden(name, '<>:"|?*/\\'):
        raise ConfigValidationError(f'{where} → file_name: недопустимое имя файла {name!r}')
    return name


def _forbidden(name: str, symbols: str) -> bool:
    has_control = any(category(character) == 'Cc' for character in name)
    return bool(set(name).intersection(symbols)) or has_control


def _validate_pattern(pattern: str, where: str) -> None:
    try:
        parts = tuple(Formatter().parse(pattern))
    except ValueError as error:
        raise ConfigValidationError(f'{where} → file_name: неверная подстановка') from error
    for _, field, spec, conversion in parts:
        if field not in (None, 'now') or spec or conversion:
            raise ConfigValidationError(f'{where} → file_name: разрешена только подстановка {{now}}')
