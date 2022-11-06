# -*- coding: utf-8 -*-
"""
configuration for database
"""
__author__ = "Kasyanov V.A."

__config = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "pass": "postgres",
    "db_name": "price_formation"
}


def get_config():
    """ get db configuration """
    return __config
