# Task-03: Services layer

## Проблема

Бизнес-логика оркестрации размазана между:

- `run.py` — `run_make_price_by_supplier()`, `run_upload_zapaska_data()`, `run_report_doubles()`
- `run_machine.py` — `_command_payload()`, `_json_parse()`, `_json_doubles()`
- `common_price.py` — `CommonPrice.parse_all_vendors()` вызывает парсинг + группировку
- `common_price_output.py` — `CommonPriceOut.write_all_prices()` + коррекция номенклатуры

Нет единого места для orchestration logic. При добавлении новой команды нужно править и `run.py`, и `run_machine.py`, и `common_price.py`.

## Решение

### 1. Создать сервисный слой в `services/`

```
services/
    __init__.py
    configure.py          ← DI-конфигурация
    service_provider.py   ← DI-контейнер
    parse_orchestrator.py ← оркестрация парсинга
    price_report.py       ← формирование отчётов/прайсов
    zapaska_service.py    ← работа с zapaska API
    doubles_service.py    ← отчёт о дублях
```

### 2. `ParseOrchestrator` — единый сервис парсинга

```python
class ParseOrchestrator:
    def __init__(
        self,
        vendor_registry: VendorRegistry,
        grouper_factory: Callable,
        config_provider: ConfigProvider,
    ): ...

    def parse_all(self) -> ParseResult:
        """Парсит всех поставщиков, группирует."""
        pass

    def parse_vendor(self, code: str) -> ParseResult:
        """Парсит одного поставщика."""
        pass
```

### 3. `PriceReportService` — генерация прайсов

```python
class PriceReportService:
    def __init__(self, writer_factory, template_registry): ...

    def write_prices(self, items, template=None) -> list[str]:
        pass

    def write_doubles(self, items) -> str:
        pass
```

### 4. Entry points становятся тонкими

```python
# run.py
def run_make_price_by_supplier(result_template=None):
    orchestrator = ServiceProvider.resolve(ParseOrchestrator)
    result = orchestrator.parse_all()
    reporter = ServiceProvider.resolve(PriceReportService)
    reporter.write_prices(result.items, template=result_template)
```

## План миграции

1. Создать `services/parse_orchestrator.py` с `ParseOrchestrator`.
2. Создать `services/price_report.py` с `PriceReportService`.
3. Переписать `run_make_price_by_supplier()` на сервисы.
4. Переписать `run_report_doubles()` на сервисы.
5. Переписать `_json_parse()` / `_json_doubles()` в `run_machine.py`.
6. Удалить `CommonPrice` (или оставить как тонкую обёртку).
7. Тесты перевести на моки сервисов.

## Критерии готовности

- [ ] `run.py` не содержит бизнес-логики — только вызов сервисов.
- [ ] `CommonPrice` не содержит orchestration (либо удалён).
- [ ] Каждая операция (parse, doubles, zapaska upload) реализована в отдельном сервисе.
- [ ] Тонкие entry points = `run.py` < 50 строк.