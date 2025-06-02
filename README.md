# LINE_DB_viewer
# LINE Database Viewer

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

A powerful GUI application for analyzing LINE database files, providing comprehensive functionality for forensic analysis and data exploration.

## Key Features

### 1. Database Connection & Management
- SQLite database file selection and connection
- WAL (Write-Ahead Logging) file analysis support
- Automatic database table detection

### 2. Table Visualization
- Dynamic table list with row counts
- Efficient batch processing for large datasets
- Alternating row colors for better readability
- Content-based column width calculation

### 3. Advanced Timestamp Processing
- Automatic timestamp detection and conversion
- Multiple timestamp format support (UNIX, WebKit, COCOA, etc.)
- Original timestamp value preservation
- Time zone conversion (JST, UTC, GMT, etc.)

### 4. Data Analysis Tools
- Detailed cell content analysis
- Binary data HEX view
- JSON data formatting and display
- Binary image data preview
- Deleted message detection and analysis

### 5. Search & Filter Capabilities
- Full-text search across all columns
- Column-specific search
- Case-sensitive search option
- NULL value handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/line-database-viewer.git
cd line-database-viewer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Launch the application:
```bash
python src/gui/gui_main.py
```

2. Select database file:
   - Click "SelectDB" button
   - Choose a LINE database file

3. Table operations:
   - Select a table from the left list
   - View table contents on the right
   - Click column headers to sort
   - Timestamp columns marked with 🕒

4. Data analysis:
   - Click cells for detailed view
   - Use search function to filter data
   - Change timestamp display format
   - Export to Excel as needed

## System Requirements

- Python 3.6 or later
- tkinter
- sqlite3
- PIL (Python Imaging Library)
- pandas (for Excel export)

## Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. Install development packages:
```bash
pip install -r requirements-dev.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## Author

Forensic Tool Developer

## Version History

- v2.0.0 (2025-06)
  - Large dataset support with batch processing
  - Improved timestamp handling
  - Enhanced UI/UX

- v1.0.0 (2025-05)
  - Initial release

---

# LINE Database Viewer (日本語)

LINEのデータベースを分析するための高機能なGUIアプリケーションです。
フォレンジック分析やデータ探索のための包括的な機能を提供します。

## 主な機能

### 1. データベース接続と管理
- SQLiteデータベースファイルの選択と接続
- WAL（Write-Ahead Logging）ファイルの解析対応
- データベーステーブルの自動検出

### 2. テーブル表示
- 行数表示付き動的テーブル一覧
- バッチ処理による大規模データセットの効率的な処理
- 読みやすさを向上させる交互の行の色
- コンテンツに基づくカラム幅の自動計算

### 3. 高度なタイムスタンプ処理
- タイムスタンプの自動検出と変換
- 複数のタイムスタンプ形式対応（UNIX、WebKit、COCOA等）
- オリジナルのタイムスタンプ値の保持
- タイムゾーン変換（日本時間、UTC、GMT等）

### 4. データ分析ツール
- セル内容の詳細分析
- バイナリデータのHEX表示
- JSONデータのフォーマットと表示
- バイナリ画像データのプレビュー
- 削除メッセージの検出と分析

### 5. 検索とフィルター機能
- 全カラムに対する全文検索
- カラム指定検索
- 大文字小文字区別オプション
- NULL値の処理

## インストール方法

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/line-database-viewer.git
cd line-database-viewer
```

2. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションを起動:
```bash
python src/gui/gui_main.py
```

2. データベースファイルを選択:
   - 「データベースの選択」ボタンをクリック
   - LINEのデータベースファイルを選択

3. テーブルの操作:
   - 左側のリストからテーブルを選択
   - テーブル内容が右側に表示
   - カラムヘッダーをクリックしてソート
   - タイムスタンプカラムは🕒アイコンで表示

4. データの分析:
   - セルをクリックして詳細表示
   - 検索機能を使用してデータをフィルタリング
   - タイムスタンプの表示形式を変更
   - 必要に応じてExcelにエクスポート

## システム要件

- Python 3.6以降
- tkinter
- sqlite3
- PIL（Python Imaging Library）
- pandas（Excelエクスポート用）

## 開発環境のセットアップ

1. 開発用の仮想環境を作成:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. 開発用パッケージをインストール:
```bash
pip install -r requirements-dev.txt
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 作者

フォレンジックツール開発者

## 更新履歴

- v2.0.0 (2025-6)
  - バッチ処理による大規模データセット対応
  - タイムスタンプ処理の改善
  - UI/UXの強化

- v1.0.0 (2025-03)
  - 初回リリース 
