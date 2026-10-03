# Быстрые команды проекта: `just` — список рецептов, `just unit -k цена` — аргументы pytest.
# Аргументы передаются без `--`, иначе он уходит в pytest как позиционный путь.
# Инструменты запускаются через `uv run`, настройки берутся из pyproject.toml / setup.cfg,
# поэтому рецепты повторяют команды из .github/workflows/python-app.yml и .pre-commit-config.yaml.

# Список рецептов
help:
    @just --list

# --- Тесты ---

# Юнит-тесты (tests/) без покрытия: быстрый цикл правки
unit *ARGS:
    uv run pytest tests --no-cov {{ARGS}}

# Интеграционные тесты (integration_tests/) без покрытия
integration *ARGS:
    uv run pytest integration_tests --no-cov {{ARGS}}

# Точечный запуск: путь файла/теста, -k, -m — без покрытия
pick *ARGS:
    uv run pytest {{ARGS}} --no-cov

# Полный прогон с покрытием (порог 95%) — как в CI
test *ARGS:
    uv run pytest {{ARGS}}

# Нагрузочные тесты (load_tests/) без xdist и порога покрытия
load *ARGS:
    uv run pytest load_tests -n0 {{ARGS}} --no-cov

# --- Приложение ---

# Интерактивное меню: just run. С аргументами — подкоманда CLI: just run parse --json
# Без --no-dev: рецепт не должен выгонять тестовые зависимости из venv.
run *ARGS:
    uv run priceformation {{ARGS}}

# --- Проверки ---

# Автоформат: black + ruff --fix
format:
    uv run black .
    uv run ruff check --fix .

# Стиль: black --check, ruff, flake8
lint:
    uv run black --check --diff .
    uv run ruff check .
    uv run flake8 .

# Типы и границы слоёв: mypy, import-linter
types:
    uv run mypy .
    uv run lint-imports

# Мёртвый код и безопасность: vulture, bandit, pip-audit
audit:
    uv run vulture
    uv run bandit -r src -c pyproject.toml
    uv run pip-audit

# Все проверки без тестов
check: lint types audit

# Полный набор перед коммитом: проверки + тесты
ci: check test
