"""Title size format variants for four_tochki sheet 1."""

from parsers.row_item.row_item import RowItem

_RUNFLAT_YES = frozenset(("да", "yes", "1", "true"))


def _size_from_parts(parts: tuple[str, str, str, str]) -> str:
    """width + postfix + height + construct_diameter."""
    width, height, postfix, construct = parts
    return "".join((width, postfix, height, construct))


def _load_velocity(row_item: RowItem) -> str:
    """Индекс нагрузки + скорости."""
    load = row_item.index_load or ""
    velocity = row_item.index_velocity or ""
    return f"{load}{velocity}"


def _join_nonempty(chunks: tuple[str, ...]) -> str:
    """Склеить куски title без пустых."""
    return " ".join(chunk for chunk in chunks if chunk)


def _extra_labels(row_item: RowItem) -> tuple[str, str]:
    """Боковина и RunFlat для title."""
    sidewall = str(row_item.inscription_on_the_side or "").strip()
    raw = str(row_item.run_flat or "").strip().lower()
    runflat = "RunFlat" if raw in _RUNFLAT_YES else ""
    return sidewall, runflat


def truck_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Title для грузовой шины."""
    sidewall = _extra_labels(row_item)[0]
    return _join_nonempty(
        (
            _size_from_parts(parts),
            mark,
            row_item.model or "",
            row_item.layering or "",
            row_item.camera_type or "",
            sidewall,
            _load_velocity(row_item),
        ),
    )


def ext_diameter_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Title с внешним диаметром."""
    size = f"{row_item.ext_diameter}x{parts[0]}{parts[3]}"
    sidewall, runflat = _extra_labels(row_item)
    return _join_nonempty(
        (
            size,
            mark,
            row_item.model or "",
            row_item.index_load or "",
            row_item.us_aff_designation or "",
            sidewall,
            runflat,
        ),
    )


def default_tire_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Обычный title легковой/спец."""
    sidewall, runflat = _extra_labels(row_item)
    return _join_nonempty(
        (
            _size_from_parts(parts),
            mark,
            row_item.model or "",
            row_item.layering or "",
            row_item.camera_type or "",
            sidewall,
            _load_velocity(row_item),
            runflat,
        ),
    )
