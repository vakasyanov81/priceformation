# 16. Title aliases через parse_paths

Подробно: [16-parse-paths-aliases-detail.md](details/16-parse-paths-aliases-detail.md)

Этап: [4. Слои и побочные эффекты](../PLAN_CLEAN_CODE.md#этап-4-слои-и-побочные-эффекты)  
Статус: не начата  
Зависит от: [14. Writer](14-writer-layers.md) (тот же запрет импорта cfg из parsers)  
Дальше: [17. Кэши процесса](17-process-caches.md)

## Зачем

`zapaska_disk_json.get_title_aliases` читает путь через `MainConfig()`. Остальной `data_provider` уже ходит в `get_parse_paths()`.

## Сделать

1. Путь к `title_aliases.json` — `get_parse_paths().config_file(...)`.
2. Убрать `from cfg.main import MainConfig` из vendor-модуля.

## Файлы

- `src/parsers/vendors/zapaska_disk_json.py`
- `src/core/parse_paths.py`
- тесты Zapaska disk title aliases, если есть

## Готово, когда

- В `zapaska_disk_json.py` нет импорта `cfg`.
- Алиасы title по-прежнему подхватываются.

## Не делать

HTTP-клиент ([15](15-zapaska-http.md)).
