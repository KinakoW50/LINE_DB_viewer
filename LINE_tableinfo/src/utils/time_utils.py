"""
時間変換ユーティリティ

このモジュールは、LINEデータベースで使用される各種タイムスタンプ形式を
変換するための関数を提供します。

主な機能：
- UNIXタイムスタンプ（マイクロ秒）からJST時間への変換
- 各種タイムスタンプフォーマットの相互変換
"""

import pytz
from datetime import datetime, timedelta
from typing import Union, Optional

def unix_micro_to_jst(unix_milli: Union[int, float]) -> str:
    """UNIXマイクロ秒タイムスタンプをJST時間に変換します。

    Args:
        unix_milli (Union[int, float]): UNIXタイムスタンプ（マイクロ秒）

    Returns:
        str: JST形式の時刻文字列（YYYY-MM-DD HH:MM:SS）
        エラーの場合はエラーメッセージを返します。

    Examples:
        >>> unix_micro_to_jst(1704034800000)
        '2024-01-01 00:00:00'
    """
    try:
        unix_seconds = unix_milli / 1000  # ミリ秒から秒に変換
        utc_time = datetime.fromtimestamp(unix_seconds, tz=pytz.UTC)
        jst = pytz.timezone('Asia/Tokyo')
        jst_time = utc_time.astimezone(jst)
        return jst_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return f"変換エラー: {e}"

def convert_timestamp(value: Union[int, float, str], format_type: str) -> str:
    """各種タイムスタンプを指定された形式に変換します。

    Args:
        value (Union[int, float, str]): 変換する値
        format_type (str): 変換後の形式
            - "JST": 日本時間（YYYY-MM-DD HH:MM:SS）
            - "UNIX": UNIXタイムスタンプ（マイクロ秒）
            - "UNIX_SEC": UNIXタイムスタンプ（秒）
            - "MAC": HFS+タイムスタンプ
            - "WEBKIT": WebKitタイムスタンプ
            - "FILETIME": Windowsファイルタイム
            - "COCOA": Cocoaタイムスタンプ

    Returns:
        str: 変換後の文字列
        エラーの場合は元の値を文字列として返します。

    Examples:
        >>> convert_timestamp(1704034800000, "JST")
        '2024-01-01 00:00:00'
        >>> convert_timestamp(1704034800000, "UNIX_SEC")
        '1704034800'
    """
    try:
        if not isinstance(value, (int, float)):
            try:
                value = int(str(value).replace('➡', ''))
            except (ValueError, TypeError):
                return str(value)

        if format_type == "JST":
            return unix_micro_to_jst(value)
        elif format_type == "UNIX":
            return str(value)
        elif format_type == "UNIX_SEC":
            return str(value // 1000000)  # マイクロ秒から秒に変換
        elif format_type == "MAC":
            # HFS+タイムスタンプ（2001年1月1日からの秒数）
            mac_epoch = datetime(2001, 1, 1, tzinfo=pytz.UTC)
            seconds = value / 1000000  # マイクロ秒から秒に変換
            dt = mac_epoch + timedelta(seconds=seconds)
            return dt.astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == "WEBKIT":
            # WebKitタイムスタンプ（1601年1月1日からのマイクロ秒）
            webkit_epoch = datetime(1601, 1, 1, tzinfo=pytz.UTC)
            seconds = value / 1000000  # マイクロ秒から秒に変換
            dt = webkit_epoch + timedelta(seconds=seconds)
            return dt.astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == "FILETIME":
            # Windowsファイルタイム（1601年1月1日からの100ナノ秒単位）
            filetime_epoch = datetime(1601, 1, 1, tzinfo=pytz.UTC)
            seconds = (value * 100) / 1000000000  # 100ナノ秒から秒に変換
            dt = filetime_epoch + timedelta(seconds=seconds)
            return dt.astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == "COCOA":
            # Cocoaタイムスタンプ（2001年1月1日からの秒数）
            cocoa_epoch = datetime(2001, 1, 1, tzinfo=pytz.UTC)
            seconds = value / 1000000  # マイクロ秒から秒に変換
            dt = cocoa_epoch + timedelta(seconds=seconds)
            return dt.astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return f"変換エラー: {str(e)}"
    
    return str(value) 