"""Title size format variants for four_tochki sheet 1."""

from parsers.nomenclature_title import compose_tire_title, load_velocity
from parsers.row_item.row_item import RowItem

_RUNFLAT_YES = frozenset(("да", "yes", "1", "true"))


def _extra_labels(row_item: RowItem) -> tuple[str, str]:
    """Боковина и RunFlat для title."""
    sidewall = str(row_item.inscription_on_the_side or "").strip()
    raw = str(row_item.run_flat or "").strip().lower()
    runflat = "RunFlat" if raw in _RUNFLAT_YES else ""
    return sidewall, runflat


def truck_title(row_item: RowItem, size: str) -> str:
    """Title для грузовой шины."""
    return compose_tire_title(
        row_item,
        size,
        row_item.layering,
        row_item.camera_type,
        _extra_labels(row_item)[0],
        load_velocity(row_item),
    )


def ext_diameter_title(row_item: RowItem, size: str) -> str:
    """Title с внешним диаметром."""
    sidewall, runflat = _extra_labels(row_item)
    return compose_tire_title(
        row_item,
        size,
        row_item.index_load,
        row_item.us_aff_designation,
        sidewall,
        runflat,
    )


def default_tire_title(row_item: RowItem, size: str) -> str:
    """Обычный title легковой/спец."""
    sidewall, runflat = _extra_labels(row_item)
    return compose_tire_title(
        row_item,
        size,
        row_item.layering,
        row_item.camera_type,
        sidewall,
        load_velocity(row_item),
        runflat,
    )
