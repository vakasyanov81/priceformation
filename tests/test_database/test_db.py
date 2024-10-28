import pathlib
import unittest
from unittest.mock import patch, MagicMock

import asyncio

from cfg.db import DBConfig
from database.db import close_db
from database.init_db import init_db_sync
from database.supplier import insert_supplier
from parsers.common_price import SupplierInfo
import sqlite3

TEST_ROOT = str(pathlib.Path(__file__).parent.absolute())


def get_db_config():
    return DBConfig(
        **{
            "host": "localhost",
            "port": 5433,
            "user_name": "postgres",
            "password": "postgres",
            "db_name": f"{TEST_ROOT}/db.sqlite3",
        }
    )


@patch("cfg.main.MainConfig.database", MagicMock(return_value=get_db_config()))
class TestDB(unittest.TestCase):

    @patch("cfg.main.MainConfig.database", MagicMock(return_value=get_db_config()))
    def setUp(self):
        init_db_sync(drop_database=True)

    def test_insert_supplier(self):
        async def check_insert():
            inserted_count = await insert_supplier(
                {
                    "10": SupplierInfo(name="test_supplier"),
                    "22": SupplierInfo(name="test_supplier_1"),
                }
            )
            assert inserted_count == 2

        asyncio.run(check_insert())

    def test_1(self):
        connection = sqlite3.connect(get_db_config().db_name)
        cursor = connection.cursor()
        sql = """
            INSERT INTO supplier (supplier_id, supplier_name)
            VALUES (?, ?) ON CONFLICT DO NOTHING RETURNING *
        """
        cursor.execute(sql, (1, "test_supplier"))
        res = cursor.fetchall()
        print(res)
        connection.commit()

    def tearDown(self):
        close_db()
        # pathlib.Path(get_db_config().db_name).unlink()
