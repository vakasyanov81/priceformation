"""
tests find manufacturer in title
"""

from typing import Any
from unittest.mock import patch

import pytest

from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.row_item.row_item import RowItem


@pytest.mark.parametrize(
    "title, title_new, manufacturer",
    [
        ("  -->    Аеолус <--  ", "--> Aeolus <--", "Aeolus"),
        ("--> БФ гудрич <--", "--> BF Goodrich <--", "BF Goodrich"),
        ("--> Sunrise <--", "--> Sunrise <--", "Sunrise"),
        ("--> RockBuster <--", "--> Rockbuster <--", "Rockbuster"),
        (
            "11.00R20 Нк.шз Кама-310 16 150/146K",
            "11.00R20 НКШЗ Кама-310 16 150/146K",
            "НКШЗ",
        ),
        (
            "Нк.шз 11.00R20 Кама-310 16 150/146K",
            "НКШЗ 11.00R20 Кама-310 16 150/146K",
            "НКШЗ",
        ),
        (
            "11.00R20 Кама-310 16 150/146K Нк.шз",
            "11.00R20 Кама-310 16 150/146K НКШЗ",
            "НКШЗ",
        ),
    ],
)
def test_replace_title_and_add_manufacturer(title: Any, title_new: Any, manufacturer: Any) -> None:
    """check replace bad manufacturer in title and add correct manufacturer in item.manufacturer"""

    row_item = RowItem({"title": title})
    ManufacturerFinder(map_manufacturer).process(row_item)

    assert row_item.title == title_new
    assert row_item.manufacturer == manufacturer


def test_blank_aliases_do_not_match_title() -> None:
    row_item = RowItem({"title": "11.00R20 some tyre 16PR"})
    ManufacturerFinder({"GhostBrand": ("", " ")}).process(row_item)

    assert row_item.title == "11.00R20 some tyre 16PR"
    assert not row_item.manufacturer


def test_longer_alias_matches_before_shorter() -> None:
    row_item = RowItem({"title": "BF Goodrich winter"})
    ManufacturerFinder({"BF": (), "BF Goodrich": ()}).process(row_item)
    assert row_item.manufacturer == "BF Goodrich"


def test_empty_alias_skips_title_replace() -> None:
    row_item = RowItem({"title": "keep title"})
    with patch(
        "parsers.base_parser.manufacturer_finder.BaseFinder.find_word_in_title",
        return_value=("Brand", ""),
    ):
        ManufacturerFinder({"Brand": ()}).process(row_item)
    assert row_item.title == "keep title"
    assert row_item.manufacturer == "Brand"


map_manufacturer = {
    "Rockbuster": (),
    "Sunrise": (),
    "Aeolus": ("Аеолус",),
    "Bridgestone": ("Бриджстоун",),
    "BF Goodrich": ("БФ гудрич", "BFGoodrich"),
    "Gislaved": ("Гиславед",),
    "Goodyear": ("ГУД-ЕАР",),
    "Doublestar": ("ДаблСтар",),
    "Dunlop": ("Данлоп",),
    "Yokohama": ("Йокохама",),
    "КирШЗ": ("Кир.ШЗ",),
    "Orium": ("Ориум",),
    "Continental": ("Континенталь",),
    "Cordiant": ("КОРДИАНТ",),
    "Kumho": ("Кумхо",),
    "Matador": ("Матадор",),
    "Michelin": ("Мишелин",),
    "Nokian": ("Нокиан",),
    "Nordman": ("Нордман",),
    "Pirelli": ("Пирелли",),
    "Roadstone": ("Роудстоун",),
    "Sava": ("Сава",),
    "Tigar": ("Тайгер",),
    "Tunga": ("ТУНГА",),
    "Firestone": ("Файрстоун",),
    "Formula": ("Формула",),
    "Hankook": ("Ханкук",),
    "НКШЗ": ("НК.ШЗ",),
    "ВолШЗ": ("Волж.ШЗ",),
    "ОШЗ": ("Омск.ШЗ",),
    "Crossleader": (),
    "Landsail": (),
    "Satoya": (),
    "Viatti": (),
    "Amtel": ("Амтел",),
    "Белшина": (
        "Белшина",
        "БШК",
    ),
    "Кама": (),
    "Kormoran": ("Корморан",),
    "Hifly": (),
    "Normaks": (),
    "ЯШЗ": ("Яр.ШЗ",),
    "Accuride": (),
    "Lemmerz": (),
    "Sant": (),
    "Nortec": (),
    "Aufine": (),
    "Forward": (),
    "Sunfull": (),
    "Алтайшина": (
        "Алтайшина",
        "АШК",
    ),
    "Power Trac": (),
    "Taitong": (),
    "Triangle": (),
    "O`Green": (),
    "Tyrex": (),
    "Haulking": (),
    "Kingnate": (),
    "FOMAN": (),
    "Maxxis": (),
    "Goodtyre": (),
    "Annaite": (
        "ANNAITE",
        "HILO",
    ),
    "Kapsen": (),
    "LongMarch": (),
    "Fronway": (),
    "Three-A": (),
    "YATAI": (),
    "Forza": (),
    "Trebl": (),
    "Yongzheng": (),
    "Н.Новгород": (),
    "ЧКПЗ": (),
    "Kabat": (),
    "Florescence": (),
    "УрШЗ": (),
    "Laufenn": (),
    "Mazzini": (),
    "Nitto": (),
    "Alcasta": (),
    "Megami": (),
    "Khomen": (),
    "Remain": (),
    "Replay": (),
}
