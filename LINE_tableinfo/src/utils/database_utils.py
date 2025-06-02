"""
データベース操作ユーティリティ

このモジュールは、LINEデータベースの操作に関する基本的な機能を提供します。
SQLiteデータベースへの接続、テーブル情報の取得、データの取得などの
機能が含まれています。

主な機能：
- データベース接続の管理
- テーブル一覧・情報の取得
- テーブルデータの取得
- 削除メッセージの検索
"""

import sqlite3
from typing import Tuple, List, Optional, Any, Dict, Set
import os

def connect_database(db_path: str) -> Tuple[Optional[sqlite3.Connection], Optional[sqlite3.Cursor]]:
    """データベースに接続します。

    Args:
        db_path (str): データベースファイルのパス

    Returns:
        Tuple[Optional[sqlite3.Connection], Optional[sqlite3.Cursor]]: 
            データベース接続とカーソルのタプル。
            エラー時はNoneのタプルを返します。

    Examples:
        >>> conn, cursor = connect_database("line.db")
        >>> if conn and cursor:
        ...     # データベース操作
        ...     conn.close()
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print(f"Database connection error: {e}")
        return None, None

def get_all_tables(cursor: sqlite3.Cursor) -> List[str]:
    """データベース内のすべてのテーブル名を取得します。

    Args:
        cursor (sqlite3.Cursor): データベースカーソル

    Returns:
        List[str]: テーブル名のリスト

    Examples:
        >>> tables = get_all_tables(cursor)
        >>> for table in tables:
        ...     print(table)
    """
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name;
    """)
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def get_table_info(cursor: sqlite3.Cursor, table_name: str) -> List[tuple]:
    """テーブルのカラム情報を取得します。

    Args:
        cursor (sqlite3.Cursor): データベースカーソル
        table_name (str): テーブル名

    Returns:
        List[tuple]: カラム情報のリスト
            各タプルは (id, name, type, notnull, default_value, primary_key) を含みます。

    Examples:
        >>> info = get_table_info(cursor, "ZMESSAGE")
        >>> for col in info:
        ...     print(f"カラム名: {col[1]}, 型: {col[2]}")
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_table_row_count(cursor: sqlite3.Cursor, table_name: str) -> int:
    """テーブルの総行数を取得します。

    Args:
        cursor (sqlite3.Cursor): データベースカーソル
        table_name (str): テーブル名

    Returns:
        int: テーブルの行数

    Examples:
        >>> count = get_table_row_count(cursor, "ZMESSAGE")
        >>> print(f"メッセージ数: {count}")
    """
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    except sqlite3.Error:
        return 0

def get_wal_data(db_path: str, table_name: str) -> List[Tuple]:
    """
    Read data from WAL file if it exists
    WALファイルが存在する場合、そのデータを読み込む
    """
    wal_path = db_path + "-wal"
    if not os.path.exists(wal_path):
        return []
    
    try:
        # WALファイル用の接続を作成（読み取り専用）
        wal_conn = sqlite3.connect(f"file:{wal_path}?mode=ro", uri=True)
        wal_cursor = wal_conn.cursor()
        
        # WALからデータを取得
        wal_cursor.execute(f"SELECT * FROM {table_name}")
        wal_data = wal_cursor.fetchall()
        
        wal_cursor.close()
        wal_conn.close()
        
        return wal_data
    except Exception as e:
        print(f"WAL reading error: {e}")
        return []

def get_table_contents_with_wal(cursor: sqlite3.Cursor, table_name: str, db_path: str, limit: Optional[int] = None) -> Tuple[List[str], List[Tuple], Set[str]]:
    """
    Get table contents including WAL data
    テーブルの内容をWALデータと共に取得
    
    Returns:
        Tuple containing:
        - List of column names
        - List of rows
        - Set of primary keys from WAL-only data
    """
    try:
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get primary key column
        cursor.execute(f"PRAGMA table_info({table_name})")
        pk_columns = [col[1] for col in cursor.fetchall() if col[5]]  # col[5] is pk flag
        
        # Get main database data
        if limit:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
        db_data = cursor.fetchall()
        
        # Get WAL data
        wal_data = get_wal_data(db_path, table_name)
        
        # Create sets of primary keys for comparison
        db_keys = set()
        wal_only_keys = set()
        
        if pk_columns:
            pk_indices = [columns.index(pk_col) for pk_col in pk_columns]
            
            # Create composite keys from main DB
            for row in db_data:
                key = tuple(row[idx] for idx in pk_indices)
                db_keys.add(key)
            
            # Process WAL data and identify new records
            for row in wal_data:
                key = tuple(row[idx] for idx in pk_indices)
                if key not in db_keys:
                    wal_only_keys.add(key)
                    db_data.append(row)
        else:
            # If no primary key, treat all WAL data as new
            db_data.extend(wal_data)
            wal_only_keys = set(range(len(db_data) - len(wal_data), len(db_data)))
        
        return columns, db_data, wal_only_keys
    
    except Exception as e:
        print(f"Error getting table contents with WAL: {e}")
        return [], [], set()

def check_deleted_messages(cursor: sqlite3.Cursor, table_name: str) -> List[tuple]:
    """削除されたメッセージを検索します。

    Args:
        cursor (sqlite3.Cursor): データベースカーソル
        table_name (str): テーブル名

    Returns:
        List[tuple]: 削除されたメッセージのリスト
            各タプルは (timestamp, text, z_pk) を含みます。

    Examples:
        >>> deleted = check_deleted_messages(cursor, "ZMESSAGE")
        >>> for msg in deleted:
        ...     print(f"削除時刻: {msg[0]}, 内容: {msg[1]}")
    """
    try:
        cursor.execute(f"""
            SELECT ZTIMESTAMP, ZTEXT, Z_PK 
            FROM {table_name} 
            WHERE Z_OPT = 1 
            AND ZTEXT IS NOT NULL 
            ORDER BY ZTIMESTAMP DESC
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"削除メッセージの検索エラー: {e}")
        return [] 

def get_table_contents(cursor: sqlite3.Cursor, table_name: str, 
                      start_pk: Optional[int] = None, 
                      end_pk: Optional[int] = None,
                      limit: Optional[int] = None) -> Tuple[List[str], List[tuple]]:
    """テーブルの内容を取得します。

    Args:
        cursor (sqlite3.Cursor): データベースカーソル
        table_name (str): テーブル名
        start_pk (Optional[int]): 開始Z_PK（指定する場合）
        end_pk (Optional[int]): 終了Z_PK（指定する場合）
        limit (Optional[int]): 取得する最大行数

    Returns:
        Tuple[List[str], List[tuple]]: 
            カラム名のリストとデータのタプルのリスト

    Examples:
        >>> columns, rows = get_table_contents(cursor, "ZMESSAGE", start_pk=1, end_pk=100)
        >>> for row in rows:
        ...     print(row)
    """
    try:
        # カラム名を取得
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # クエリを構築
        query = f"SELECT * FROM {table_name}"
        if start_pk is not None and end_pk is not None:
            query += f" WHERE Z_PK BETWEEN {start_pk} AND {end_pk}"
        if limit is not None:
            query += f" LIMIT {limit}"
            
        # データを取得
        cursor.execute(query)
        rows = cursor.fetchall()
        
        return columns, rows
    except sqlite3.Error as e:
        print(f"テーブル内容の取得エラー: {e}")
        return [], [] 