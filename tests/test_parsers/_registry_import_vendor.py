"""Стоб-модуль вендора для проверки импорта из `_VENDORS_TO_IMPORT`.

Используется в test_all_vendors_from_registry_populates_when_empty:
модуль не должен быть уже импортирован, чтобы importlib.import_module
заново выполнил регистрацию.
"""

from parsers.registry import register_vendor
from tests.test_parsers.test_registry import _FakeBaseParser


@register_vendor('_test_import_vendor')
class ImportTestVendor(_FakeBaseParser):
    """Регистрируется при импорте модуля."""
