"""Title size format variants for four_tochki sheet 1."""

from parsers.row_item.row_item import RowItem


def _size_from_parts(parts: tuple[str, str, str, str]) -> str:
    """width + postfix + height + construct_diameter."""
    width, height, postfix, construct = parts
    return "".join((width, postfix, height, construct))


def _load_velocity(row_item: RowItem) -> str:
    """Индекс нагрузки + скорости."""
    load = row_item.index_load or ""
    velocity = row_item.index_velocity or ""
    return "{0}{1}".format(load, velocity)


def truck_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Title для грузовой шины."""
    size = _size_from_parts(parts)
    return " ".join((size, mark, row_item.model or "", _load_velocity(row_item)))


def ext_diameter_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Title с внешним диаметром."""
    size = "{0}x{1}{2}".format(row_item.ext_diameter, parts[0], parts[3])
    model = row_item.model or ""
    index_load = row_item.index_load or ""
    designation = row_item.us_aff_designation or ""
    return " ".join((size, mark, model, index_load, designation))


def default_tire_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Обычный title легковой/спец."""
    size = _size_from_parts(parts)
    chunks = (
        size,
        mark,
        row_item.model or "",
        row_item.layering or "",
        row_item.camera_type or "",
        _load_velocity(row_item),
    )
    return " ".join(chunks)
