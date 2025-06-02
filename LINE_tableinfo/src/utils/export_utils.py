"""
Excel export utility module for LINE Database Viewer

This module provides functionality to export database table contents
to Excel format.
"""

import os
from datetime import datetime
import pandas as pd
import sqlite3
from typing import Optional

def export_to_excel(cursor: sqlite3.Cursor, table_name: str) -> Optional[str]:
    """
    Export table contents to Excel file.
    
    Args:
        cursor (sqlite3.Cursor): Database cursor
        table_name (str): Name of the table to export
        
    Returns:
        Optional[str]: Path to the exported Excel file if successful, None otherwise
    """
    try:
        # テーブルの内容を取得
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            return None
            
        # カラム名を取得
        columns = [description[0] for description in cursor.description]
        
        # DataFrameを作成
        df = pd.DataFrame(rows, columns=columns)
        
        # 出力ディレクトリを作成
        output_dir = "exports"
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名を生成（テーブル名と現在時刻）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = os.path.join(output_dir, f"{table_name}_{timestamp}.xlsx")
        
        # Excelファイルに出力
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        return excel_file
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None 