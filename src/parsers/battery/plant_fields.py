"""Очистка особенностей входных колонок прайса План-Т до доменной валидации."""

from domain.product_group_handler import InputFields


def normalize_fields(fields: InputFields) -> dict[str, object]:
    """Убрать сноску гарантии; известное мусорное значение оставить неизвестным."""
    prepared = dict(fields)
    warranty = fields.get('warranty_months')
    if isinstance(warranty, str):
        normalized = warranty.strip()
        prepared['warranty_months'] = None if normalized == 'ъъъ0,5' else normalized.removeprefix('*')
    return prepared
