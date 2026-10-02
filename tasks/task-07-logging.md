# Task-07: Logging через logging.Logger

## Проблема

В проекте используются глобальные функции `log_msg`, `err_msg`, `warn_msg` из `infrastructure.logging.log_message`. Они:

1. **Не иерархические** — нельзя настроить уровень логирования для конкретного модуля.
2. **Смешивают ответственность** — функция и пишет в консоль, и в файл, и в JSON.
3. **Нефильтруемые** — `need_print_log` — костыль для подавления вывода в JSON-режиме.
4. **Затрудняют тестирование** — чтобы проверить лог, нужно мокать глобальную функцию.
5. **Спам в коде** — `log_msg("...", need_print_log=True)` размазан по всем модулям.

## Решение

### 1. Переход на `logging.Logger` с именами `__name__`

```python
# infrastructure/logging/log_setup.py

import logging

_LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'


def setup_logging(level=logging.INFO, log_dir: str | None = None):
    """Настроить корневой логгер."""
    handlers = [logging.StreamHandler()]
    if log_dir:
        handlers.append(logging.FileHandler(...))
    logging.basicConfig(
        level=level,
        format=_LOG_FORMAT,
        handlers=handlers,
    )
```

### 2. В каждом модуле — `logger = logging.getLogger(__name__)`

```python
# parsers/common_price.py
logger = logging.getLogger(__name__)


class CommonPrice:
    def parse_vendor(self, parser: BaseParser):
        try:
            ...
        except Exception as exc:
            logger.error('Ошибка разбора %s: %s', parser, exc)
            raise
```

### 3. JSON-режим через отдельный handler

```python
class JsonModeFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not _json_mode_active.get()


# Переключение:
def set_json_mode(active: bool) -> None:
    _json_mode_active.set(active)
```

### 4. `infrastructure/logging/log_message.py` — удалить или оставить как фасад

Если оставить — фасад должен просто проксировать в логгер:

```python
def log_msg(msg: str, level=logging.INFO) -> None:
    logging.getLogger('priceformation').log(level, msg)
```

## План миграции

1. Создать `infrastructure/logging/log_setup.py` с настройкой логгера.
2. В `init_cfg()` вызывать `setup_logging()`.
3. Пройти по всем модулям:
   - Добавить `logger = logging.getLogger(__name__)`
   - Заменить `log_msg("текст")` → `logger.info("текст")`
   - Заменить `err_msg(...)` → `logger.error(...)`
   - Заменить `warn_msg(...)` → `logger.warning(...)`
4. Переписать JSON-режим: вместо `set_print_quiet` — `logging.disable(logging.WARNING)` или свой Filter.
5. Удалить `need_print_log` из вызовов (теперь это настройка handler'а).
6. Удалить `infrastructure/logging/log_message.py` (или оставить как deprecation wrapper).
7. Поправить тесты — заменить моки `log_msg` на проверки через `caplog`.

## Что сделано

- Пакет `infrastructure/logging/` разложен по ролям:
  - `log_setup.py` — `setup_logging(paths, level)`: консоль всегда, файлы при известных путях; повторный
    вызов снимает только свои обработчики (помечены `__SETUP_MARK__`), чужие (pytest) не трогает;
  - `console.py` — `ConsoleHandler` и форматтер: пишет в **текущий** `sys.stdout` (в момент `emit`),
    поэтому `capsys`/`redirect_stdout` работают; INFO — голое сообщение, остальные уровни с префиксом
    `[LEVEL]:` и цветом; фильтры `JsonModeFilter` и `FileOnlyFilter`;
  - `file_logging.py` — два файловых обработчика (`log_<date>.log` для INFO+, `error_<date>.log` для ERROR)
    с `delay=True`; недоступная папка не ломает запуск — остаётся консоль;
  - `json_mode.py` — `set_json_mode()`/`json_mode_active()` (состояние в `ContextVar`) и контекст-менеджер
    `quiet_console()` вместо глобального флага `set_print_quiet`; `run_machine.machine_json` оборачивает
    команду в `with quiet_console():`;
  - `log_resolve.py` — подписи и цвета уровней для форматтера.
- Traceback домена (`domain/exception_log.py` → `exception_logging.write_exception_log`) пишется как
  `logger.error(..., extra={FILE_ONLY: True})`: в файле есть, в консоли пользователя нет.
- Декоратор `@logging` из `infrastructure/logging/wrappers.py` пишет детали вызова на DEBUG
  (в консоль не попадают), traceback ошибки — WARNING.
- `infrastructure/logging/log_message.py` удалён.
- Тесты проверяют логи через `caplog`; `tests/test_architecture_markers.py` запрещает возврат
  глобальных log-функций.

## Критерии готовности

- [x] Нигде не импортируется `log_msg`, `err_msg`, `warn_msg`, `print_log`.
- [x] Все модули используют `logging.getLogger(__name__)`.
- [x] JSON-режим не выводит логи благодаря настройке handler'а, не через глобальный флаг.
- [x] Тесты проверяют логи через `caplog` (pytest built-in).
- [x] `infrastructure/logging/log_message.py` удалён или помечен как deprecated.
