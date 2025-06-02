import unittest
import sqlite3
import os
from src.utils.database_utils import (
    connect_database,
    get_all_tables,
    get_table_info,
    get_table_row_count
)

class TestDatabaseUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # テスト用のデータベースを作成
        cls.test_db = "test.db"
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        # テストテーブルを作成
        cursor.execute("""
            CREATE TABLE test_table (
                Z_PK INTEGER PRIMARY KEY,
                ZTIMESTAMP INTEGER,
                ZTEXT TEXT
            )
        """)
        
        # テストデータを挿入
        cursor.execute("""
            INSERT INTO test_table (Z_PK, ZTIMESTAMP, ZTEXT)
            VALUES (1, 1704034800000, 'テストメッセージ')
        """)
        
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        # テスト用データベースを削除
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_connect_database(self):
        conn, cursor = connect_database(self.test_db)
        self.assertIsNotNone(conn)
        self.assertIsNotNone(cursor)
        conn.close()

    def test_get_all_tables(self):
        conn, cursor = connect_database(self.test_db)
        tables = get_all_tables(cursor)
        self.assertIn('test_table', tables)
        conn.close()

    def test_get_table_info(self):
        conn, cursor = connect_database(self.test_db)
        info = get_table_info(cursor, 'test_table')
        column_names = [col[1] for col in info]
        self.assertIn('Z_PK', column_names)
        self.assertIn('ZTIMESTAMP', column_names)
        self.assertIn('ZTEXT', column_names)
        conn.close()

    def test_get_table_row_count(self):
        conn, cursor = connect_database(self.test_db)
        count = get_table_row_count(cursor, 'test_table')
        self.assertEqual(count, 1)
        conn.close()

if __name__ == '__main__':
    unittest.main() 