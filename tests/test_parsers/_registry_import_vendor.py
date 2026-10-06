"""Стаб-модуль вендора для проверки импорта (обратная совместимость).

Используется в старых тестах реестра; при полном переходе на конфиги
может быть удалён вместе с ``test_registry.py``.
"""

from parsers.registry import register_vendor


@register_vendor('_test_import_vendor')
class ImportTestVendor:
    """Регистрируется при импорте модуля."""
