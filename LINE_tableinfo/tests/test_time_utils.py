import unittest
from src.utils.time_utils import unix_micro_to_jst, convert_timestamp

class TestTimeUtils(unittest.TestCase):
    def test_unix_micro_to_jst(self):
        # 2024-01-01 00:00:00 JST
        timestamp = 1704034800000
        expected = "2024-01-01 00:00:00"
        result = unix_micro_to_jst(timestamp)
        self.assertEqual(result, expected)

    def test_convert_timestamp(self):
        # UNIXタイムスタンプ（マイクロ秒）
        timestamp = 1704034800000
        
        # JST変換
        jst_result = convert_timestamp(timestamp, "JST")
        self.assertEqual(jst_result, "2024-01-01 00:00:00")
        
        # UNIX（マイクロ秒）
        unix_result = convert_timestamp(timestamp, "UNIX")
        self.assertEqual(unix_result, str(timestamp))
        
        # UNIX（秒）
        unix_sec_result = convert_timestamp(timestamp, "UNIX_SEC")
        self.assertEqual(unix_sec_result, str(timestamp // 1000000))

if __name__ == '__main__':
    unittest.main() 