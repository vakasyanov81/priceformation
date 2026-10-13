"""Golden-регрессия README §11: реальные строки прайсов, тип и сверка с поставщиком.

`golden_rows.json` — снапшот реальных строк (сгенерирован из `file_prices/`,
которые в git не коммитятся). Тест ловит регрессии классификатора и
`declared_matches` на данных, а не только на выдуманных кейсах.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.product_types import declared_matches

_GOLDEN_PATH = Path(__file__).parent / 'golden_rows.json'
_DEFINED_TYPES = {
    'Легковая шина',
    'Легкогрузовая шина',
    'Грузовая шина',
    'Спецшина',
    'Автокамера',
    'Ободная лента',
    'Уплотнительное кольцо',
    'Диск',
}


def _load_rows() -> list[dict[str, Any]]:
    raw = json.loads(_GOLDEN_PATH.read_text(encoding='utf-8'))
    return cast(list[dict[str, Any]], raw['rows'])


def _golden_ids(count: int) -> list[str]:
    """Числовые ASCII-идентификаторы кейсов.

    mutmut 3.8 не переваривает не-ASCII nodeid параметризованных тестов:
    передаёт их без `[...]` и получает «not found».
    """
    return ['golden-' + str(index).zfill(2) for index in range(count)]


_ROWS = _load_rows()
_IDS = _golden_ids(len(_ROWS))


@pytest.mark.parametrize('case', _ROWS, ids=_IDS)
def test_golden_row_type_and_correction(case: dict[str, Any]) -> None:
    """Независимый тип и признак расхождения совпадают со снапшотом."""
    title = case['title']
    own = ProductTypeClassifier().classify(RowItem({'title': title}))
    assert own == case['own'], title
    corrected = not declared_matches(case['declared'], own)
    assert corrected is case['corrected'], title


def test_golden_covers_all_defined_types() -> None:
    """Снапшот покрывает каждый канонический тип, кроме мото (его нет в прайсах)."""
    covered = {case['own'] for case in _ROWS}
    assert covered >= _DEFINED_TYPES
    assert '' not in covered


def test_golden_has_cross_family_corrections() -> None:
    """В снапшоте есть расхождения между семьями (не только легковая↔легкогрузовая)."""
    corrected = [case for case in _ROWS if case['corrected']]
    assert len(corrected) >= 10
