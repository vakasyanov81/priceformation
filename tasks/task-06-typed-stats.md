# Task-06: Typed parser stats

## Проблема

В `common_price.py` и `base_parser_row.py` используется `getattr` для чтения полей статистики у парсера:

```python
# common_price.py
skips = getattr(parser, 'unknown_category_skips', ())
count = getattr(parser, 'black_list_skips', 0)

# base_parser_row.py
parser.black_list_skips += 1  # может не быть
```

Это:
- **Нетипизировано** — `mypy` / `pyright` не видит полей.
- **Хрупко** — если парсер не выставил поле, тихая ошибка.
- **Неявный контракт** — неясно, какие поля обязан иметь парсер.

## Решение

### 1. `ParserStats` — TypedDict или dataclass

```python
@dataclass
class ParserStats:
    """Статистика работы парсера за один прогон."""

    black_list_skips: int = 0
    unknown_category_skips: list[str] = field(default_factory=list)

    def merge(self, other: ParserStats) -> None:
        self.black_list_skips += other.black_list_skips
        self.unknown_category_skips.extend(other.unknown_category_skips)
```

### 2. `BaseParser` имеет `stats: ParserStats`

```python
class BaseParser:
    def __init__(self, ...):
        self.stats = ParserStats()
        ...
    
    def parse(self) -> list[RowItem]:
        ...
        return self.get_parsed_items()
```

### 3. `CommonPrice` работает со `stats`

```python
class CommonPrice:
    def parse_vendor(self, parser: BaseParser) -> None:
        try:
            parsed = parser.parse()
        except ...
        else:
            self._total_stats.merge(parser.stats)
```

### 4. `_keep_row_item` использует `parser.stats`

```python
def _keep_row_item(parser: BaseParser, row_item: RowItem) -> bool:
    if row_item.rest_count and not row_item.price_opt:
        return False
    if not row_item.title or parser.is_valid_title(row_item.title):
        return True
    parser.stats.black_list_skips += 1
    return False
```

## План миграции

1. Создать `ParserStats` в `parsers/base_parser/parse_statistic.py` или отдельно.
2. Заменить `self.unknown_category_skips: list[str] = []` и `self.black_list_skips = 0` на `self.stats = ParserStats()`.
3. Поправить методы, инкрементирующие/читающие эти поля.
4. Убрать `getattr` из `common_price.py`.
5. Обновить `ParseResultStatistic` (если нужно — переименовать/объединить).

## Критерии готовности

- [ ] Нигде в коде нет `getattr(parser, "black_list_skips", 0)` или аналогичных.
- [ ] `BaseParser.stats` типизирован как `ParserStats`.
- [ ] Поля статистики доступны через автокомплит IDE.
- [ ] `mypy` / `pyright` на `src/` не ругается на неизвестные атрибуты.