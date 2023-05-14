# -*- coding: utf-8 -*-
"""
configuration for database
"""
__author__ = "Kasyanov V.A."

from typing import NamedTuple


class DBConfig(NamedTuple):
    host: str
    port: str
    user_name: str
    password: str
    db_name: str


def get_config() -> DBConfig:
    """get db configuration"""

    return DBConfig(
        **{
            "host": "localhost",
            "port": 5433,
            "user_name": "postgres",
            "password": "postgres",
            "db_name": "/home/huck/projects/priceformation_web/src/db.sqlite3"
            # "db_name": __PROJECT_ROOT__
            # + os.sep
            # + __FILE_PRICES__
            # + os.sep
            # + "price_formation.db",
        }
    )
