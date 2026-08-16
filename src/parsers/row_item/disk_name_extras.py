"""Разбор хвостов названия диска: завод, вентиль, футорка."""

import re

_FACTORY_RE = re.compile(r"\(([A-Za-z]{2,5})\)")
_ALIVE = "alive"
_OUTER_VALVE = "наруж. вентиль"
_INNER_VALVE = "внутр. вентиль"
_HUB_ADAPTER = "под футорку"
_WITH_VALVE_MARK = "с вент"
_WITH_VALVE = "с вент."
_RING = "(кольцо)"
_DISK_MARKERS = (
    (_ALIVE, _ALIVE),
    (_OUTER_VALVE, _OUTER_VALVE),
    (_INNER_VALVE, _INNER_VALVE),
    (_HUB_ADAPTER, _HUB_ADAPTER),
    (_WITH_VALVE_MARK, _WITH_VALVE),
    (_RING, _RING),
)


def disk_name_extras(title: str) -> str:
    """Завод, alive, вентиль и хвосты диска; без толщины и складского кода."""
    if not title:
        return ""
    lowered = title.lower()
    factories = ("({0})".format(code) for code in _FACTORY_RE.findall(title))
    extras = (label for needle, label in _DISK_MARKERS if needle in lowered)
    return " ".join((*factories, *extras))
