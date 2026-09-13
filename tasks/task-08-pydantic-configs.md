# Task-08: Pydantic для конфигов

## Проблема

Конфигурация читается везде через `json.loads` → `dict[str, Any]` → `cast()`:

```python
raw_rules = cast(dict[str, dict[str, Any]], raw_rules)
```

Это:
- **Нет валидации** — ошибка в JSON формате проявится позже (или не проявится вообще).
- **Нет автокомплита** — IDE не подсказывает ключи.
- **Cast-спагетти** — `cast(dict[str, dict[str, Any]], raw_rules)` — ложное чувство безопасности.
- **Нет дефолтов** — `raw.get("min_recommended_percent_markup") or 0` — костыль.

## Решение

### 1. Pydantic-модели для всех конфигов

```python
from pydantic import BaseModel, Field


class MarkUpRule(BaseModel):
    min: float = 0
    max: float = 0
    percent_markup: float = 0
    percent: float | None = None  # alias for percent_markup


class AbsoluteMarkUpRules(BaseModel):
    min_absolute_markup: float = 0
    markup_percent: float = 0
    mode: Literal['multiplier', 'delta'] = 'multiplier'


class MarkupRulesConfig(BaseModel):
    markup_rules: dict[str, MarkUpRule] = {}
    min_recommended_percent_markup: float = 0
    max_recommended_percent_markup: float = 0
    absolute_markup_rules: AbsoluteMarkUpRules = AbsoluteMarkUpRules()
    replace_small_recommended: bool = False
```

### 2. Провайдеры возвращают модели, не dict

```python
class MarkupRulesProviderBase:
    def get_markup_data(self) -> MarkupRulesConfig:
        raise NotImplementedError


class MarkupRulesProviderFromUserConfig(MarkupRulesProviderBase):
    def get_markup_data(self) -> MarkupRulesConfig:
        raw = self._read_json()
        return MarkupRulesConfig.model_validate(raw)
```

### 3. Валидация на границе

```python
try:
    config = MarkupRulesConfig.model_validate(raw)
except ValidationError as exc:
    raise ConfigValidationError(f'Ошибка в {file}: {exc}')
```

### 4. Убираем `extract_markup_rules()` и `markup_params_from_rule()`

Эти функции были костылями для ручного парсинга dict → NamedTuple. Pydantic делает это автоматически.

## План миграции

1. Добавить `pydantic` в зависимости (если нет) — `pydantic>=2`.
2. Создать `parsers/data_provider/models.py` с Pydantic-моделями.
3. Перевести `MarkupRulesProviderBase` и реализации на Pydantic.
4. Перевести `VendorListProviderBase` и реализации на Pydantic.
5. Перевести `BlackListProviderBase` и реализации (здесь может быть список строк — это и так ок).
6. Перевести `ManufacturerAliasesProviderBase` и реализации.
7. Удалить старые NamedTuple: `MarkUpParams`, `MarkupRules`, `AbsoluteMarkUpRules`, `VendorParams`.
8. Удалить `extract_markup_rules()` и `markup_params_from_rule()`.
9. Поправить тесты.

## Критерии готовности

- [ ] Все конфиги проходят валидацию Pydantic при загрузке.
- [ ] Ошибка в JSON поставщика → `ConfigValidationError`, не cryptic `KeyError`.
- [ ] Старые NamedTuple удалены.
- [ ] `cast(dict[str, ...], ...)` сведён к минимуму в проекте.
- [ ] IDE подсказывает поля при работе с конфигами.