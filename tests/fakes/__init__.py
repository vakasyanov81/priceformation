"""Тестовые дубли: читатели и writer-драйвер, которые не ходят в диск.

Живут вне `src/`, чтобы не попадать в колесо (`only-include = ["src"]`).
Импорт: `from tests.fakes.fake_xls_reader import FakeXlsReader` — корень `tests/`
в `sys.path` ставит `tests/conftest.py`.
"""
