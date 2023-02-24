# -*- coding: utf-8 -*-
"""
tests for Poshk vendor after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

from parsers.base_parser.base_parser import BasePriceParseConfiguration
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_rest import ZapaskaRestParser
from parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.zapaska import zapaska_2file_result

from .test_parse_zapaska import parser_config


def get_fake_parser(rest_result, parse_result):
    """get fake parser"""

    def make_result(_self):
        return rest_result.get(_self.file_path)

    FakeXlsReader.parse_result = make_result

    return ZapaskaRestParser(
        xls_reader=FakeXlsReader,
        file_prices=list(rest_result.keys()),
        price_mrp=parse_result,
        price_config=BasePriceParseConfiguration(parser_config),
    )


def test_2files():
    """test combine result from two price file"""
    rest_result, parse_result = zapaska_2file_result()

    result: List[RowItem] = get_fake_parser(rest_result, parse_result).get_result()

    assert len(result) == 2

    res = [
        {
            "code": "00002",
            "codes": ["00002"],
            "hash_title": "4d454469fa9bb61110e92a2317896b91",
            "percent": 22.12,
            "price_markup": 4900.0,
            "price_purchase": 4012.4,
            "price_recommended": 4201.0,
            "rest_count": 17.0,
            "sup_name": "Запаска (остатки)",
            "title": "00 Сельх.шины",
            "type_production": "",
        },
        {
            "code": "00003",
            "codes": ["00003"],
            "hash_title": "d25c14e72f2a951230173b9a68f9d294",
            "percent": 22.12,
            "price_markup": 4900,
            "price_purchase": 4012.4,
            "price_recommended": 4251.0,
            "rest_count": 10.0,
            "sup_name": "Запаска (остатки)",
            "title": "00 Сельх.шины__1",
            "type_production": "",
        },
    ]

    assert result[0].to_dict() == res[0]
    assert result[1].to_dict() == res[1]
