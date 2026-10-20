"""Бренд и модель для названия номенклатуры."""

from domain.row_item.row_item import RowItem

_BRAND_SEPARATORS = (' ', '-')


def brand_label(row_item: RowItem) -> str:
    """Бренд для title как в поле: регистр бренда (`BFGoodrich`, `XCMG`) не меняется."""
    return (row_item.identity.manufacturer or '').strip()


def _brand_rest(model: str, brand: str) -> str | None:
    """Остаток модели после бренда в начале (`Ikon Character` → `Character`) или None, если бренда там нет."""
    rest = model[len(brand) :]
    starts_with_brand = bool(brand) and model.lower().startswith(brand.lower())
    if starts_with_brand and rest[:1] in _BRAND_SEPARATORS:
        return rest.lstrip(' -').strip()
    return None


def model_label(row_item: RowItem) -> str:
    """Модель для title без бренда в начале: `Ikon Character Eco C2` → `Character Eco C2`, `КАМА-NF 701` → `NF 701`."""
    model = (row_item.identity.model or '').strip()
    return _brand_rest(model, brand_label(row_item)) or model
