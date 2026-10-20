"""Подстановка переменных окружения в JSON-настройки: ``"${MAIL_SENDER_STK}"`` → значение из .env.

Так в файлах настроек под git остаются ссылки, а личные данные (адреса почты и т.п.) живут в ``.env``.
"""

import re
from collections.abc import Mapping
from typing import Any

from domain.exceptions import ConfigValidationError

type Env = Mapping[str, str]
type JsonObject = dict[str, Any]
type JsonList = list[Any]

_PLACEHOLDER = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}')


def expand_env(raw: Any, env: Env, where: str) -> Any:
    """Заменить ``${NAME}`` во всех строках JSON; переменной нет или она пуста — ошибка с путём до ключа."""
    if isinstance(raw, dict):
        return _expand_object(raw, env, where)
    if isinstance(raw, list):
        return _expand_list(raw, env, where)
    if isinstance(raw, str):
        return _expand_text(raw, env, where)
    return raw


def _expand_object(raw: JsonObject, env: Env, where: str) -> JsonObject:
    expanded: JsonObject = {}
    for key, nested in raw.items():
        expanded[key] = expand_env(nested, env, f'{where} → {key}')
    return expanded


def _expand_list(raw: JsonList, env: Env, where: str) -> JsonList:
    expanded: JsonList = []
    for index, nested in enumerate(raw):
        expanded.append(expand_env(nested, env, f'{where}[{index}]'))
    return expanded


def _expand_text(raw: str, env: Env, where: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return _env_value(match.group(1), env, where)

    return _PLACEHOLDER.sub(replace, raw)


def _env_value(name: str, env: Env, where: str) -> str:
    env_value = env.get(name, '').strip()
    if not env_value:
        raise ConfigValidationError(f'{where}: не задана переменная окружения «{name}» (укажите её в .env)')
    return env_value
