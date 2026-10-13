"""Загрузка переменных окружения из файла .env в корне проекта."""

import os
from pathlib import Path

from domain.config_context import get_config_provider

_DEFAULT_FILENAME = '.env'


def parse_dotenv_line(raw_line: str) -> tuple[str, str] | None:
    """Разобрать строку .env в пару ключ-значение; мусорные строки — None."""
    line = raw_line.strip()
    if not line or line.startswith('#') or '=' not in line:
        return None
    key, _, raw_value = line.partition('=')
    key = key.strip()
    if not key:
        return None
    return key, raw_value.strip().strip("'").strip('"')


def load_dotenv(env_path: Path | None = None) -> bool:
    """Прочитать .env в os.environ (существующие ключи не перезаписываются)."""
    path = env_path or Path(get_config_provider().project_root) / _DEFAULT_FILENAME
    if not path.is_file():
        return False

    for raw_line in path.read_text(encoding='utf-8').splitlines():
        parsed = parse_dotenv_line(raw_line)
        if parsed is None:
            continue
        key, env_value = parsed
        if key not in os.environ:
            os.environ[key] = env_value
    return True
