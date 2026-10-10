"""Стратегия слота `title` для Пошка: сборка названия шины в порядке Пионера."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.poshk_title import PoshkTireCompose


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
            '10.00R20 DOUBLEROAD DR-801 149/146K 18PR унив.ось с об/л',
        ),
        (
            '11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)',
            '11R22.5 TAITONG HS103 146/143M 16PR вед.ось',
        ),
        (
            '11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт',
            '11.00R20 НКШЗ И-68А 150/146K 16PR',
        ),
        (
            '12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт',
            '12.4L-16 БШК Бел-160М 111A6 8PR сельхозшина',
        ),
    ],
)
def test_poshk_tire_compose_glues_in_pioner_order(raw: str, expected: str) -> None:
    """Пошк: параметры пересобираются в порядок Пионера."""
    assert PoshkTireCompose().prepare(RowItem({'title': raw})) == expected


def test_poshk_tire_compose_is_idempotent() -> None:
    """Повторная сборка уже собранного названия не меняет результат."""
    strategy = PoshkTireCompose()
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт'})

    once = strategy.prepare(row)
    twice = strategy.prepare(row)

    assert once == twice == '10.00R20 DOUBLEROAD DR-801 149/146K 18PR унив.ось с об/л'


def test_poshk_tire_compose_falls_back_to_normalize_for_disk() -> None:
    """Диск не размер шины: работает обычная нормализация размера."""
    row = RowItem({'title': 'Диск штамп NORTEC-16 11.75*22.5 10*335 ET0 d281 , шт'})

    assert PoshkTireCompose().prepare(row) == 'Диск штамп NORTEC-16 11.75x22.5 10x335 ET0 d281'


def test_poshk_tire_compose_empty_title_stays_empty() -> None:
    """Пустой title не превращается в заглушку."""
    assert PoshkTireCompose().prepare(RowItem({})) == ''


def test_poshk_tire_compose_ship_without_brand_uses_fallback_brand() -> None:
    """Ведущая «Шина» без бренда отдаётся нормализации с брендом-заглушкой."""
    strategy = PoshkTireCompose(fallback_brand='Алтайшина', brand_probe=lambda _title: False)

    prepared = strategy.prepare(RowItem({'title': 'Шина 11.00R20 И-111А 16PR 150/146K TT, шт'}))

    assert prepared == 'Алтайшина 11.00R20 И-111А 16PR 150/146K TT'


def test_poshk_tire_compose_ship_with_brand_is_composed() -> None:
    """Ведущая «Шина» с известным брендом разбирается и пересобирается."""
    strategy = PoshkTireCompose(fallback_brand='Алтайшина', brand_probe=lambda _title: True)

    prepared = strategy.prepare(RowItem({'title': 'Шина 10.00R20 FORWARD Traction-310 16PR 146/143K TT, шт'}))

    assert prepared == '10.00R20 FORWARD Traction-310 146/143K 16PR TT'
