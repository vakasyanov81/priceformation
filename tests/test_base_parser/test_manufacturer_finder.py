# -*- coding: utf-8 -*-
"""
tests find manufacturer in title
"""
__author__ = "Kasyanov V.A."

import pytest

from src.parsers.base_parser.manufacturer_finder import ManufacturerFinder
from src.parsers.row_item.row_item import RowItem


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
def test_replace_title_and_add_manufacturer(title, title_new, manufacturer):
    """check replace bad manufacturer in title and add correct manufacturer in item.manufacturer"""

    item = RowItem({"title": title})
    ManufacturerFinder(map_manufacturer).process(item)

    assert item.title == title_new
    assert item.manufacturer == manufacturer


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
