# Task-04: Composition over Inheritance в BaseParser

## Проблема

Текущая иерархия наследования `BaseParser`:

```
BaseParser
  └── ParserFileReader
        └── ParserRowHooks
              └── ParserRestPolicy
                    └── ParserMarkupOps
                          └── ParserTitleFilters
```

Это 6 уровней. Каждый класс добавляет свою группу методов, но все они работают через промежуточные protected-поля (`_markup_policy`, `_category_finder`, `_manufacturer_finder`, `_black_list`). Это:

- **Нарушает SRP** — класс знает про чтение, REST, наценку, категории, производителей, фильтры.
- **Усложняет тестирование** — нужно замокать 6 уровней или поднять всю иерархию.
- **Затрудняет расширение** — новая фича = ещё один уровень наследования.
- **Запутывает типы** — `ParserRowHooks.find_manufacturer_on_enrich: ClassVar[bool]` наследуется всем.

## Решение

### Композиция: `BaseParser` собирается из стратегий

```python
class BaseParser:
    """Парсер — композиция стратегий."""

    def __init__(
        self,
        parse_config: ParseConfiguration | None = None,
        *,
        file_reader: FileReaderProtocol,
        markup_policy: MarkupPolicy,
        row_processor: RowProcessorProtocol,
        category_finder: CategoryFinder,
        title_filters: TitleFilterProtocol,
        price_source: PriceSource | None = None,
    ):
        self._file_reader = file_reader
        self._markup_policy = markup_policy
        self._row_processor = row_processor
        self._category_finder = category_finder
        self._title_filters = title_filters
        ...
```

### Интерфейсы (Protocols)

```python
class FileReaderProtocol(Protocol):
    def read_rows(self, paths: list[str]) -> list[dict[str, Any]]: ...
    def map_items(self, raw_rows: list[dict]) -> list[RowItem]: ...


class RowProcessorProtocol(Protocol):
    def enrich(self, items: list[RowItem]) -> list[RowItem]: ...
    def filter_keep(self, items: list[RowItem]) -> list[RowItem]: ...


class TitleFilterProtocol(Protocol):
    def is_valid_title(self, title: str) -> bool: ...
    def set_prepared_title(self, row_item: RowItem) -> None: ...
    def get_spike_title(self, row_item: RowItem) -> str: ...
```

### Вендоры подмешивают только свою специфику

```python
class PoshkParser(BaseParser):
    """Парсер Пошк — только специфичные хуки."""
    
    def after_row_mapped(self, row_item: RowItem) -> None:
        # специфичная логика PosHk
        row_item.type_production = self._parse_type(row_item.title)
```

## План миграции

1. Выделить протоколы для каждой стратегии в `parsers/base_parser/protocols.py`.
2. Создать `FileReader`, `RowProcessor`, `TitleFilter` как реализации по умолчанию.
3. Переписать `BaseParser.__init__` на композицию.
4. Перенести код из `ParserFileReader → FileReader` (без наследования).
5. Перенести код из `ParserRowHooks → RowProcessor`.
6. Перенести код из `ParserRestPolicy → RowProcessor`.
7. Перенести код из `ParserMarkupOps → MarkupPolicy` (часть уже там).
8. Перенести код из `ParserTitleFilters → TitleFilter`.
9. Удалить старые классы иерархии.
10. Поправить тесты.

## Критерии готовности

- [ ] `BaseParser` не наследуется от цепочки `ParserFileReader → ... → ParserTitleFilters`.
- [ ] Все функциональные блоки (читатель, обработчик строк, фильтры) — отдельные классы/протоколы.
- [ ] Вендоры могут подменять любую стратегию через конструктор.
- [ ] Тесты `test_base_parser_process.py` проходят без изменений логики.
- [ ] Добавление нового поведения не требует правки `BaseParser`.