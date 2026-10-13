"""Провайдер настроек почты: parse_config/mail.json с кэшем на путь."""

from functools import lru_cache
from pathlib import Path

from domain.config_context import get_config_provider
from infrastructure.data.file_reader import read_json_file
from parsers.mail.errors import MailConfigNotFoundError
from parsers.mail.models import MailConfig

_CONFIG_NAME = 'mail.json'


@lru_cache(maxsize=1)
def _load_config(path: str) -> MailConfig:
    """Прочитать и разобрать файл настроек; файла нет — понятная ошибка."""
    if not Path(path).is_file():
        raise MailConfigNotFoundError(f'Не найден файл настроек почты: {path}')
    return MailConfig.from_dict(read_json_file(path), Path(path).name)


def load_mail_config() -> MailConfig:
    """Настройки почты из parse_config/mail.json."""
    return _load_config(get_config_provider().config_file(_CONFIG_NAME))


def clear_mail_config_cache() -> None:
    """Сбросить кэш настроек почты (после смены провайдера путей или правки файла)."""
    _load_config.cache_clear()
