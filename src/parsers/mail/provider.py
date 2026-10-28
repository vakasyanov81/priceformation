"""Провайдер настроек почты: parse_config/mail.json с кэшем на путь.

Строки вида ``${MAIL_SENDER_STK}`` заменяются значениями из .env / окружения: адреса отправителей
не хранятся в файле настроек.
"""

import os
from functools import lru_cache
from pathlib import Path

from domain.config_context import get_config_provider
from domain.mail import MailConfigNotFoundError
from infrastructure.config.dotenv import load_dotenv
from infrastructure.config.env_placeholders import expand_env
from infrastructure.data.file_reader import read_json_file
from parsers.mail.models import MailConfig

_CONFIG_NAME = 'mail.json'


@lru_cache(maxsize=1)
def _load_config(path: str) -> MailConfig:
    """Прочитать и разобрать файл настроек; файла нет — понятная ошибка."""
    if not Path(path).is_file():
        raise MailConfigNotFoundError(f'Не найден файл настроек почты: {path}')
    load_dotenv()
    where = Path(path).name
    return MailConfig.from_dict(expand_env(read_json_file(path), os.environ, where), where)


def load_mail_config() -> MailConfig:
    """Настройки почты из parse_config/mail.json."""
    return _load_config(get_config_provider().config_file(_CONFIG_NAME))


def clear_mail_config_cache() -> None:
    """Сбросить кэш настроек почты (после смены провайдера путей или правки файла)."""
    _load_config.cache_clear()
