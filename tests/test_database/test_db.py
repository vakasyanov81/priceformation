import asyncio
import pathlib
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from src.cfg.db import DBConfig
from src.database.db import close_db
from src.database.init_db import init_db_sync
from src.database.supplier import insert_supplier

TEST_ROOT = str(pathlib.Path(__file__).parent.parent.absolute())


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


@patch("src.cfg.main.MainConfig.database", MagicMock(return_value=get_db_config()))
class TestDB(unittest.TestCase):

    @patch("src.cfg.main.MainConfig.database", MagicMock(return_value=get_db_config()))
    def setUp(self):
        init_db_sync(drop_database=True)

    def _test_insert_supplier(self):
        async def check_insert():
            inserted_count = await insert_supplier(
                {
                    "10": "test_supplier",
                    "22": "test_supplier_1",
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
        cursor.fetchall()
        connection.commit()

    def tearDown(self):
        close_db()
        # pathlib.Path(get_db_config().db_name).unlink()
