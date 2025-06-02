"""
LINE Database Viewer GUI Module

A powerful and user-friendly GUI application for analyzing LINE database contents.
This viewer provides comprehensive functionality for forensic analysis and data exploration.

Main Features:
1. Database Connection and Management
   - SQLite database file selection and connection
   - Support for WAL (Write-Ahead Logging) file analysis
   - Automatic detection of database tables

2. Table Visualization
   - Dynamic table list display with row counts
   - Efficient handling of large datasets with batch processing
   - Alternating row colors for better readability
   - Custom column width calculation based on content

3. Advanced Timestamp Handling
   - Automatic timestamp detection and conversion
   - Multiple timestamp format support (UNIX, WebKit, COCOA, etc.)
   - Original timestamp value preservation
   - Time zone conversion (JST, UTC, GMT, etc.)

4. Data Analysis Tools
   - Detailed cell content analysis
   - Binary data visualization with hex view
   - JSON data formatting and display
   - Image preview for binary image data
   - Deleted message detection and analysis

5. Search and Filter Capabilities
   - Full-text search across all columns
   - Column-specific search
   - Case-sensitive search option
   - NULL value handling

6. Export Functionality
   - Excel export with formatting
   - Data preservation for forensic analysis

7. User Interface Features
   - Progress indication for long operations
   - Responsive design for large datasets
   - Detailed information display
   - Error handling and user notifications

Technical Details:
- Written in Python using tkinter
- SQLite3 database support
- Optimized for performance with large datasets
- Memory-efficient data handling
- Cross-platform compatibility

Usage:
1. Launch the application
2. Select a LINE database file
3. Choose a table from the list
4. Explore and analyze the data
5. Use the search and filter tools as needed
6. Export data when required

Requirements:
- Python 3.6 or later
- tkinter
- sqlite3
- PIL (Python Imaging Library)
- pandas (for Excel export)

Author: R/Y
Version: 2.0.0
Last Updated: 2025/6

JP======

LINE データベースビューアー

このビューアーは、LINEのデータベースを分析するための高機能なGUIアプリケーションです。
フォレンジック分析やデータ探索のための包括的な機能を提供します。

主な機能：
1. データベース接続と管理
   - SQLiteデータベースファイルの選択と接続
   - WAL（Write-Ahead Logging）ファイルの解析対応
   - データベーステーブルの自動検出

2. テーブル表示
   - 行数表示付き動的テーブル一覧
   - バッチ処理による大規模データセットの効率的な処理
   - 読みやすさを向上させる交互の行の色
   - コンテンツに基づくカラム幅の自動計算

3. 高度なタイムスタンプ処理
   - タイムスタンプの自動検出と変換
   - 複数のタイムスタンプ形式対応（UNIX、WebKit、COCOA等）
   - オリジナルのタイムスタンプ値の保持
   - タイムゾーン変換（日本時間、UTC、GMT等）

4. データ分析ツール
   - セル内容の詳細分析
   - バイナリデータのHEX表示
   - JSONデータのフォーマットと表示
   - バイナリ画像データのプレビュー
   - 削除メッセージの検出と分析

5. 検索とフィルター機能
   - 全カラムに対する全文検索
   - カラム指定検索
   - 大文字小文字区別オプション
   - NULL値の処理

6. エクスポート機能
   - フォーマット付きExcelエクスポート
   - フォレンジック分析用データ保存

7. ユーザーインターフェース機能
   - 長時間操作の進捗表示
   - 大規模データセット用の応答性の高い設計
   - 詳細情報表示
   - エラー処理とユーザー通知

技術詳細：
- Pythonとtkinterを使用
- SQLite3データベース対応
- 大規模データセット用に最適化
- メモリ効率の良いデータ処理
- クロスプラットフォーム対応

使用方法：
1. アプリケーションを起動
2. LINEデータベースファイルを選択
3. テーブル一覧から対象を選択
4. データの探索と分析
5. 必要に応じて検索やフィルターを使用
6. 必要に応じてデータをエクスポート

必要要件：
- Python 3.6以降
- tkinter
- sqlite3
- PIL（Python Imaging Library）
- pandas（Excelエクスポート用）

作者：R/Y
バージョン：2.0.0
最終更新：2025/6
"""

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
import os
from typing import Optional, List, Tuple, Dict, Any
import sys
from pathlib import Path
import json
import io
from PIL import Image, ImageTk

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.database_utils import (
    connect_database,
    get_all_tables,
    get_table_info,
    get_table_row_count,
    get_table_contents,
    get_table_contents_with_wal,
    check_deleted_messages
)
from src.utils.time_utils import convert_timestamp
from src.utils.export_utils import export_to_excel

class TimeFormatMenu(tk.Menu):
    """
    GUI_Timestampmenu
    タイムスタンプ表示形式GUI
    """

    def __init__(self, parent: tk.Widget, column_name: str, callback: callable):
        """
        Args:
            parent (tk.Widget): parent widget/親ウィジェット
            column_name (str): select column/対象のカラム名
            callback (callable): callback function/形式変更時のコールバック関数
        """
        super().__init__(parent, tearoff=0)
        self.callback = callback
        self.column_name = column_name
        
        # 日本時間関連
        self.add_command(
            label="JST (日本時間)", 
            command=lambda: self.callback(column_name, "JST")
        )
        self.add_separator()
        
        # UNIXタイムスタンプ関連
        self.add_command(
            label="UNIX_microsecond (マイクロ秒)", 
            command=lambda: self.callback(column_name, "UNIX_microsecond")
        )
        self.add_command(
            label="UNIX_millisecond (ミリ秒)", 
            command=lambda: self.callback(column_name, "UNIX_millisecond")
        )
        self.add_command(
            label="UNIX_second (秒)", 
            command=lambda: self.callback(column_name, "UNIX_second")
        )
        self.add_separator()
        
        # プラットフォーム固有
        self.add_command(
            label="MAC (HFS+)", 
            command=lambda: self.callback(column_name, "MAC")
        )
        self.add_command(
            label="COCOA", 
            command=lambda: self.callback(column_name, "COCOA")
        )
        self.add_command(
            label="FILETIME (Windows)", 
            command=lambda: self.callback(column_name, "FILETIME")
        )
        self.add_separator()
        
        # Webブラウザ関連
        self.add_command(
            label="WebKit", 
            command=lambda: self.callback(column_name, "WEBKIT")
        )
        self.add_command(
            label="Chrome (WebKit)", 
            command=lambda: self.callback(column_name, "CHROME")
        )
        self.add_command(
            label="Firefox", 
            command=lambda: self.callback(column_name, "FIREFOX")
        )
        self.add_separator()
        
        # その他のタイムゾーン
        self.add_command(
            label="UTC (世界協定時)", 
            command=lambda: self.callback(column_name, "UTC")
        )
        self.add_command(
            label="GMT (グリニッジ標準時)", 
            command=lambda: self.callback(column_name, "GMT")
        )

class LineDBViewer(tk.Tk):
    """
    Main window LINE Database Viewer

    LINEデータベースビューアのメインウィンドウ
    
    """

    def __init__(self):
        """
        Main window initialization
        メインウィンドウの初期化
        """
        super().__init__()

        self.title("LINE Database Viewer")
        self.geometry("1200x800")

        # WALデータ関連の初期化
        self.wal_records = set()  # WALのみに存在するレコードのキー
        
        # 時間表示モードの初期化
        self.time_display_modes: Dict[str, str] = {}
        
        # オリジナル値保存用の辞書
        self.original_values_cache: Dict[str, Dict[str, str]] = {}
        
        # データベース接続情報の初期化
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.current_db_path: Optional[str] = None
        
        # UIの作成
        self.create_widgets()
        self.current_data: List[Any] = []
        
        # ツリービューのタグを設定
        self._configure_tree_tags()

    def connect_database(self, db_path: Optional[str] = None) -> bool:
        """
        　　Connect to the database
            データベースに接続

        Args:
            db_path (Optional[str]): DB_pathデータベースファイルのパス

        Returns:
            bool: 接続成功の場合:True
        """
        if db_path:
            # 既存の接続を閉じる
            if self.conn:
                self.cursor.close()
                self.conn.close()
            
            # 新しい接続を作成
            self.conn, self.cursor = connect_database(db_path)
            if self.conn and self.cursor:
                self.current_db_path = db_path
                
                # テーブル一覧を更新
                self.tables = get_all_tables(self.cursor)
                self.table_rows = {}
                for table in self.tables:
                    self.table_rows[table] = get_table_row_count(self.cursor, table)
                
                # テーブルリストを更新
                self.update_table_list()
                return True
            return False

    def create_widgets(self):
        """
        UI_Widget_creation
        UIウィジェットの作成
        """
        # メインフレーム
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左側フレーム（テーブル一覧とテーブル情報）
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)  # サイズを固定

        # データベース選択セクション
        self._create_database_section(left_frame)
        
        # テーブル一覧セクション
        self._create_table_list_section(left_frame)
        
        # テーブル情報セクション
        self._create_table_info_section(left_frame)
        
        # 操作ボタンセクション
        self._create_operation_section(left_frame)

        # 右側フレーム（テーブル表示）
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 検索セクション
        self._create_search_section(right_frame)

        # テーブル表示セクション
        self._create_table_view_section(right_frame)

        # ステータスバーの初期化
        self.status_label = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_database_section(self, parent: ttk.Frame):
        """
        Create database selection section
        データベース選択画面の作成
        """
        db_section = ttk.LabelFrame(parent, text="DB/データベース")
        db_section.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(db_section, text="SelectDB/データベースの選択", 
                  command=self.select_database).pack(fill=tk.X, padx=5, pady=5)
        
        self.db_path_label = ttk.Label(db_section, text="CurrentDB/表示中DB: None", 
                                     wraplength=280)
        self.db_path_label.pack(fill=tk.X, padx=5, pady=(0, 5))

    def _create_table_list_section(self, parent: ttk.Frame):
        """
        TableList
        テーブル一覧セクションを作成
        """
        table_section = ttk.LabelFrame(parent, text="TableList/テーブル一覧")
        table_section.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        table_list_frame = ttk.Frame(table_section)
        table_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        table_scrollbar = ttk.Scrollbar(table_list_frame)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.table_listbox = tk.Listbox(table_list_frame, 
                                      yscrollcommand=table_scrollbar.set)
        self.table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar.config(command=self.table_listbox.yview)

        # テーブル選択時のイベントをバインド
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)

    def _create_table_info_section(self, parent: ttk.Frame):
        """
        Create table information section
        テーブル情報セクション
        """
        info_section = ttk.LabelFrame(parent, text="TableInfo/テーブル情報")
        info_section.pack(fill=tk.BOTH, pady=(0, 5))

        info_text_frame = ttk.Frame(info_section)
        info_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        info_scrollbar = ttk.Scrollbar(info_text_frame)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_text = scrolledtext.ScrolledText(
            info_text_frame, 
            wrap=tk.WORD, 
            height=10,
            yscrollcommand=info_scrollbar.set
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.config(command=self.info_text.yview)

    def _create_operation_section(self, parent: ttk.Frame):
        """
        Create operation button section
        操作ボタン情報
        """
        button_section = ttk.LabelFrame(parent, text="Operations/操作項目")
        button_section.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(button_section, text="テーブル分析", 
                  command=self.analyze_table).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(button_section, text="欠損データの確認", 
                  command=self.check_deleted).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(button_section, text="表示テーブルのExcel出力", 
                  command=self.export_excel).pack(fill=tk.X, padx=5, pady=2)

    def _create_search_section(self, parent: ttk.Frame):
        """
        Create Search section
        検索セクションを作成
        """
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        # 上部フレーム（検索条件）
        top_frame = ttk.Frame(search_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        # 検索エントリー
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            top_frame, 
            textvariable=self.search_var,
            width=40
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))

        # カラム選択
        self.search_column_var = tk.StringVar(value="All/すべて")
        self.column_combo = ttk.Combobox(
            top_frame,
            textvariable=self.search_column_var,
            state='readonly',
            width=15
        )
        self.column_combo.pack(side=tk.LEFT, padx=5)

        # 検索条件選択
        self.search_condition_var = tk.StringVar(value="Include/含む")
        condition_combo = ttk.Combobox(
            top_frame,
            textvariable=self.search_condition_var,
            values=["完全一致", "前方一致", "後方一致", "含む"],
            state='readonly',
            width=10
        )
        condition_combo.pack(side=tk.LEFT, padx=5)

        # 下部フレーム（オプション）
        bottom_frame = ttk.Frame(search_frame)
        bottom_frame.pack(fill=tk.X)

        # 大文字/小文字を区別
        self.case_sensitive_var = tk.BooleanVar(value=False)
        case_check = ttk.Checkbutton(
            bottom_frame,
            text="大文字/小文字を区別",
            variable=self.case_sensitive_var,
            command=self._perform_search
        )
        case_check.pack(side=tk.LEFT)

        # NULL値を含める
        self.include_null_var = tk.BooleanVar(value=True)
        null_check = ttk.Checkbutton(
            bottom_frame,
            text="NULL値を含める",
            variable=self.include_null_var,
            command=self._perform_search
        )
        null_check.pack(side=tk.LEFT, padx=10)

        # 検索ボタン
        search_button = ttk.Button(
            bottom_frame,
            text="Search/検索",
            command=self._perform_search
        )
        search_button.pack(side=tk.LEFT, padx=5)

        # クリアボタン
        clear_button = ttk.Button(
            bottom_frame,
            text="Clear/クリア",
            command=self._clear_search
        )
        clear_button.pack(side=tk.LEFT)

        # 検索結果カウンター
        self.search_count_label = ttk.Label(bottom_frame, text="")
        self.search_count_label.pack(side=tk.RIGHT)

        # 検索エントリーにバインド
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
        self.search_entry.bind('<KeyRelease>', lambda e: self._perform_search())

    def _create_table_view_section(self, parent: ttk.Frame):
        """
        TableViewSection
        テーブル表示セクションを作成
        """
        table_view_section = ttk.LabelFrame(parent, text="TableViewテーブル内容")
        table_view_section.pack(fill=tk.BOTH, expand=True)

        # スタイルの設定
        style = ttk.Style()
        style.configure("Treeview", 
                       rowheight=25,            # 行の高さ
                       borderwidth=1,           # ボーダー幅
                       relief="solid",          # ボーダーのスタイル
                       font=('TkDefaultFont', 10))  # フォント設定
        
        # ヘッダーのスタイル設定
        style.configure("Treeview.Heading",
                       borderwidth=1,           # ヘッダーのボーダー幅
                       relief="solid",          # ヘッダーのボーダースタイル
                       font=('TkDefaultFont', 10, 'bold'),  # ヘッダーのフォント
                       background="SystemButtonFace",  # ヘッダーの背景色
                       foreground="black")      # ヘッダーのテキスト色
        
        # グリッド線の色を設定
        style.configure("Treeview", 
                       background="white",      # 背景色
                       fieldbackground="white", # フィールドの背景色
                       foreground="black")      # テキストの色

        # 水平方向に分割するPanedWindow
        h_paned = ttk.PanedWindow(table_view_section, orient=tk.HORIZONTAL)
        h_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # テーブル表示用フレーム（左側）
        tree_frame = ttk.Frame(h_paned)
        h_paned.add(tree_frame, weight=3)  # 幅の比率を3に設定

        # ツリービューのスクロールバー
        tree_y_scrollbar = ttk.Scrollbar(tree_frame)
        tree_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree_x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # ツリービュー
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_y_scrollbar.set,
            xscrollcommand=tree_x_scrollbar.set,
            selectmode='browse',  # 1行のみ選択可能
            style="Treeview"     # スタイルを適用
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # グリッド線を表示（show="tree headings"にすると縦線も表示）
        self.tree["show"] = "headings"  # ヘッダーのみ表示（左の階層ツリーは非表示）

        tree_y_scrollbar.config(command=self.tree.yview)
        tree_x_scrollbar.config(command=self.tree.xview)

        # 詳細表示用フレーム（右側）
        detail_frame = ttk.LabelFrame(h_paned, text="DetailView/詳細表示")
        h_paned.add(detail_frame, weight=1)  # 幅の比率を1に設定

        # タブコントロールの作成
        self.detail_notebook = ttk.Notebook(detail_frame)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 基本情報タブ
        self.basic_detail_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.basic_detail_frame, text='BasicInfo/基本情報')
        
        # 基本情報用のテキストエリア
        self.detail_text = scrolledtext.ScrolledText(
            self.basic_detail_frame,
            wrap=tk.WORD,
            width=40,
            height=10
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # 拡張情報タブ
        self.extended_detail_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.extended_detail_frame, text='ExtendedInfo/拡張情報')  # デフォルトのタブ名
        # データ形式に応じてタブ名を動的に変更するメソッドを追加
        def update_extended_tab_name(data_type: str):
            tab_names = {
                "bplist": "BPList解析",
                "binary": "バイナリ解析", 
                "json": "JSON解析",
                "timestamp": "タイムスタンプ解析",
                "text": "テキスト解析"
            }
            tab_name = tab_names.get(data_type, "拡張情報")
            self.detail_notebook.tab(self.extended_detail_frame, text=tab_name)
        self.update_extended_tab_name = update_extended_tab_name
        
        # 拡張情報用のテキストエリア
        self.extended_detail_text = scrolledtext.ScrolledText(
            self.extended_detail_frame,
            wrap=tk.WORD,
            width=40,
            height=10
        )
        self.extended_detail_text.pack(fill=tk.BOTH, expand=True)

        # HEX表示タブ
        self.hex_detail_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.hex_detail_frame, text='HEX/HEX表示')
        
        # HEX表示用のテキストエリア
        self.hex_detail_text = scrolledtext.ScrolledText(
            self.hex_detail_frame,
            wrap=tk.NONE,  # 折り返しなし
            width=40,
            height=10,
            font=('Courier', 9)  # 等幅フォントを使用
        )
        self.hex_detail_text.pack(fill=tk.BOTH, expand=True)

        # 画像表示タブ
        self.image_detail_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(self.image_detail_frame, text='Image/画像表示')
        
        # 画像表示用のフレーム（ボタンとキャンバスを含む）
        image_display_frame = ttk.Frame(self.image_detail_frame)
        image_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # ボタンフレーム
        button_frame = ttk.Frame(image_display_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 表示切替ボタン
        self.show_full_image_var = tk.BooleanVar(value=False)
        self.toggle_image_button = ttk.Button(
            button_frame,
            text="ShowAll/全て表示",
            command=self._toggle_image_display
        )
        self.toggle_image_button.pack(side=tk.LEFT)
        
        # 画像表示用のキャンバス
        self.image_canvas = tk.Canvas(
            image_display_frame,
            width=300,
            height=300,
            bg='white'
        )
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 画像情報表示用のラベル
        self.image_info_label = ttk.Label(
            image_display_frame,
            text="",
            wraplength=280,
            justify=tk.LEFT
        )
        self.image_info_label.pack(fill=tk.X, padx=5, pady=5)

        # イベントバインド
        self.tree.bind('<Button-1>', self.on_tree_click)

    def select_database(self):
        """
        Select database file
        選択するDBの定義
        """
        file_path = filedialog.askopenfilename(
            title="Select Database/データベースの選択",
            filetypes=[
                ("SQLite Database", "*.db;*.sqlite;*.sqlite3;*.db3"),
                ("DB File", "*.db"),
                ("SQLite File", "*.sqlite"),
                ("SQLite3 File", "*.sqlite3"),
                ("DB3 File", "*.db3"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            if self.connect_database(file_path):
                # Show progress bar
                progress_window = tk.Toplevel(self)
                progress_window.title("Loading")
                progress_window.geometry("300x50")
                progress_window.transient(self)
                progress_window.grab_set()
                
                progress_label = ttk.Label(progress_window, text="Loading database...")
                progress_label.pack(pady=(5,0))
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(fill=tk.X, padx=20, pady=5)
                progress_bar.start(10)
                
                progress_window.update()
                progress_window.destroy()
                
                self.db_path_label.config(text=f"CurrentDB/表示中DB: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Failed to load database")

    def update_table_list(self):
        """
        Update table list
        テーブル一覧の更新
        """
        self.table_listbox.delete(0, tk.END)
        for table in self.tables:
            row_count = self.table_rows.get(table, 0)
            self.table_listbox.insert(tk.END, f"{table} ({row_count:,} rows)")

    def get_selected_table(self, clear_display: bool = True) -> Optional[str]:
        """
        SelectTablename
        選択されたテーブル名を取得
        """
        selection = self.table_listbox.curselection()
        if not selection:
            if clear_display:
                messagebox.showwarning("Warning/警告", "Selectable/テーブルを選択してください")
            return None
        
        table_text = self.table_listbox.get(selection[0])
        table_name = table_text.split(" (")[0]  # 行数の部分を除去
        
        if clear_display:
            self.info_text.delete('1.0', tk.END)
        
        return table_name

    def analyze_table(self):
        """
        AnalyzeTable
        テーブルの分析を行い、情報を表示
        """
        table_name = self.get_selected_table()
        if not table_name:
            return

        try:
            # テーブル情報を取得
            columns = get_table_info(self.cursor, table_name)
            row_count = get_table_row_count(self.cursor, table_name)
            
            # 分析結果を表示
            result_lines = [
                f"=== {table_name} テーブル内訳表示 ===",
                f"総レコード数: {row_count:,}",
                "\nカラム情報:",
                "-" * 40
            ]
            
            # カラムごとのサンプルデータを取得
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample_data = self.cursor.fetchone()
            
            for i, col in enumerate(columns):
                col_id, name, type_name, notnull, default_val, pk = col
                sample_value = sample_data[i] if sample_data else None
                
                # タイムスタンプの場合は変換
                if sample_value and self.is_timestamp_column(name):
                    try:
                        sample_value = convert_timestamp(sample_value, "JST")
                    except:
                        pass  # 変換に失敗した場合は元の値を使用
                
                col_info = [
                    f"- {name} ({type_name})",
                    f"  {'[主キー] ' if pk else ''}"
                    f"{'[NOT NULL] ' if notnull else ''}"
                ]
                
                if sample_value is not None:
                    col_info.append(f"  サンプル値: {sample_value}")
                
                result_lines.extend(col_info)
            
            self.update_result_text("\n".join(result_lines))
            
        except Exception as e:
            messagebox.showerror("Error", f"テーブル分析エラー: {e}")

    def check_deleted(self):
        """
        Check deleted messages
        欠損データの確認
        """
        table_name = self.get_selected_table()
        if not table_name:
            return

        try:
            # Get deleted messages
            deleted_messages = check_deleted_messages(self.cursor, table_name)
            
            if deleted_messages:
                result_lines = [
                    "=== Deleted Messages ===",
                    "-" * 40
                ]
                
                for timestamp, text, z_pk in deleted_messages:
                    result_lines.extend([
                        f"ID: {z_pk}",
                        f"Time: {convert_timestamp(timestamp, 'JST')}",
                        f"Content: {text}",
                        "-" * 40
                    ])
                
                result_lines.append(f"\nTotal: {len(deleted_messages)} deleted messages found")
            else:
                result_lines = ["No deleted messages found"]
            
            self.update_result_text("\n".join(result_lines))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error checking deleted messages: {e}")

    def export_excel(self):
        """
        Export to Excel file
        Excel出力
        """
        table_name = self.get_selected_table()
        if not table_name:
            return

        try:
            # Execute export
            excel_file = export_to_excel(self.cursor, table_name)
            
            if excel_file:
                messagebox.showinfo("Success", f"Data exported to Excel file:\n{excel_file}")
            else:
                messagebox.showerror("Error", "Export failed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to Excel: {e}")

    def update_result_text(self, text: str):
        """
        UpdateResultText
        結果テキストを更新
        """
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, text)

    def on_tree_click(self, event):
        """
        TreeClick
        ツリービューのクリックイベント処理
        """
        region = self.tree.identify('region', event.x, event.y)
        if region == "cell":
            # クリックされたセルの情報を取得
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if not item or not column:
                return
            
            # 前回の選択をクリア
            self._clear_selection_highlights()
            
            # 行全体を選択
            self.tree.item(item, tags=['selected_row'])
            
            # クリックされたセルの情報を取得
            col_num = int(column.replace('#', '')) - 1  # '#1'から1を取得し、0ベースのインデックスに変換
            col_name = self.tree["columns"][col_num]    # カラム名を取得
            value = self.tree.set(item, col_name)       # 値を取得
            
            # セルをハイライト
            current_tags = list(self.tree.item(item).get('tags', []))
            if 'selected_cell' not in current_tags:
                current_tags.append('selected_cell')
            self.tree.item(item, tags=current_tags)
            
            # 詳細表示を更新
            self._update_detail_view(col_name, value, item)

    def _clear_selection_highlights(self):
        """
        ClearSelectHighlights
        選択のハイライトをクリア
        """
        for item in self.tree.get_children():
            current_tags = list(self.tree.item(item).get('tags', []))
            if 'selected_row' in current_tags:
                current_tags.remove('selected_row')
            if 'selected_cell' in current_tags:
                current_tags.remove('selected_cell')
            self.tree.item(item, tags=current_tags)

    def _update_detail_view(self, column_name: str, value: Any, item_id: str):
        """
        UpdateDetailView
        詳細ビューを更新
        """
        try:
            # データタイプの判定
            data_type = self._detect_data_type(column_name, value)
            
            # 基本情報の更新
            self._update_basic_detail(column_name, value, item_id)
            
            # 拡張情報の更新
            self._update_extended_detail(column_name, value, data_type)
            
            # HEX表示の更新
            self._update_hex_detail(value, data_type)
            
            # 画像プレビューの更新
            self._update_image_preview(value)
            
        except Exception as e:
            self._show_error_in_details(f"Error/詳細表示エラー: {e}")

    def _detect_data_type(self, column_name: str, value: Any) -> str:
        """
        ExtractDatetype
        データタイプを検出
        """
        if self.is_timestamp_column(column_name):
            return "timestamp"
        elif isinstance(value, str) and value.startswith("bplist"):
            return "bplist"
        elif isinstance(value, (bytes, bytearray)):
            return "binary"
        elif isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
            return "json"
        else:
            return "text"

    def _update_basic_detail(self, column_name: str, value: Any, item_id: str):
        """
        UpdateBasicDetail
        基本情報タブの更新
        """
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete('1.0', tk.END)
        
        # ヘッダー情報
        self.detail_text.insert(tk.END, "=== BasicInfo基本情報 ===\n\n", 'header')
        
        # カラム情報
        self.detail_text.insert(tk.END, f"カラム名: {column_name}\n", 'field')
        self.detail_text.insert(tk.END, "-" * 40 + "\n\n")
        
        # 値の表示（基本情報）
        if value is not None:
            if self.is_timestamp_column(column_name):
                try:
                    # キャッシュから元の値を取得
                    original_values = self.original_values_cache.get(item_id, {})
                    if original_values:
                        col_index = self.tree["columns"].index(column_name)
                        original_value = original_values.get(col_index)
                        
                        if original_value is not None:
                            self.detail_text.insert(tk.END, "オリジナル値:\n", 'field')
                            self.detail_text.insert(tk.END, f"{original_value}\n\n", 'value')
                    
                    self.detail_text.insert(tk.END, "時刻 (JST):\n", 'field')
                    self.detail_text.insert(tk.END, f"{value}\n", 'value')
                except Exception as e:
                    print(f"Error in timestamp display: {e}")
                    self.detail_text.insert(tk.END, "値:\n", 'field')
                    self.detail_text.insert(tk.END, f"{value}\n", 'value')
            else:
                self.detail_text.insert(tk.END, "値:\n", 'field')
                self.detail_text.insert(tk.END, f"{str(value)[:1000]}\n", 'value')
                if len(str(value)) > 1000:
                    self.detail_text.insert(tk.END, "...(省略)...\n", 'info')
        else:
            self.detail_text.insert(tk.END, "値: NULL\n", 'null')
        
        # 行の位置情報
        try:
            row_position = len(self.tree.get_children()[:self.tree.index(item_id)]) + 1
            self.detail_text.insert(tk.END, "\n--- レコード情報 ---\n", 'header')
            self.detail_text.insert(tk.END, f"レコード番号: {row_position}\n", 'info')
        except Exception:
            pass  # 行位置の取得に失敗した場合は無視
        
        self._apply_text_styles(self.detail_text)
        self.detail_text.config(state=tk.DISABLED)

    def _update_extended_detail(self, column_name: str, value: Any, data_type: str):
        """
        UpdateExtendeDetail
        拡張情報タブの更新"""
        self.extended_detail_text.config(state=tk.NORMAL)
        self.extended_detail_text.delete('1.0', tk.END)
        
        self.extended_detail_text.insert(tk.END, f"=== ExtendedInfo/拡張情報 ({data_type}) ===\n\n", 'header')
        
        try:
            if data_type == "bplist":
                self._show_bplist_details(value)
            elif data_type == "binary":
                self._show_binary_details(value)
            elif data_type == "json":
                self._show_json_details(value)
            elif data_type == "timestamp":
                self._show_timestamp_details(value)
            else:
                self._show_text_details(value)
        except Exception as e:
            self.extended_detail_text.insert(tk.END, f"拡張情報の解析に失敗しました: {e}\n", 'error')
        
        self._apply_text_styles(self.extended_detail_text)
        self.extended_detail_text.config(state=tk.DISABLED)

    def _show_bplist_details(self, value: str):
        """
        BpilistDetails
        bplistデータの詳細表示
        """
        self.extended_detail_text.insert(tk.END, "bplistデータ解析:\n", 'field')
        try:
            # bplistデータの解析処理をここに実装
            # 必要に応じて外部ライブラリを使用
            self.extended_detail_text.insert(tk.END, "データ形式: バイナリPlist\n", 'info')
            self.extended_detail_text.insert(tk.END, "サイズ: " + str(len(value)) + " bytes\n", 'info')
            # 解析結果の表示
        except Exception as e:
            self.extended_detail_text.insert(tk.END, f"bplistの解析に失敗: {e}\n", 'error')

    def _show_binary_details(self, value: bytes):
        """
        GUI_Binarydetails
        バイナリデータの詳細表示
        """
        self.extended_detail_text.insert(tk.END, "バイナリデータ解析:\n", 'field')
        self.extended_detail_text.insert(tk.END, f"サイズ: {len(value)} bytes\n\n", 'info')

        # 16進数ダンプとASCII表示を生成
        BYTES_PER_LINE = 16
        offset = 0
        
        while offset < len(value):
            # オフセットを表示
            self.extended_detail_text.insert(tk.END, f"{offset:08x}  ", 'offset')
            
            chunk = value[offset:offset + BYTES_PER_LINE]
            hex_values = []
            ascii_values = []
            
            # 16進数とASCII文字を生成
            for i, byte in enumerate(chunk):
                hex_values.append(f"{byte:02x}")
                # 表示可能なASCII文字の場合はその文字を、それ以外は'.'を表示
                ascii_values.append(chr(byte) if 32 <= byte <= 126 else '.')
                
                # 8バイトごとに空白を追加
                if i == 7:
                    hex_values.append('')
            
            # 16進数部分の表示（不足分はスペースで埋める）
            hex_line = ' '.join(hex_values)
            hex_line = hex_line.ljust(49)  # 16*2 + 15 + 1 (spaces) + 1 (middle space)
            self.extended_detail_text.insert(tk.END, hex_line + " │ ", 'hex')
            
            # ASCII部分の表示
            ascii_line = ''.join(ascii_values)
            self.extended_detail_text.insert(tk.END, ascii_line, 'ascii')
            self.extended_detail_text.insert(tk.END, "\n")
            
            offset += BYTES_PER_LINE
            
            # 表示行数を制限（最初の256バイトまで）
            if offset >= 256:
                self.extended_detail_text.insert(tk.END, "\n... (残りは省略) ...\n", 'info')
                self.extended_detail_text.insert(tk.END, "[全て表示]", 'link')
                break

    def _show_json_details(self, value: str):
        """
        JSONDetails
        JSONデータの詳細表示
        """
        try:
            json_data = json.loads(value)
            formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
            self.extended_detail_text.insert(tk.END, "JSON構造:\n", 'field')
            self.extended_detail_text.insert(tk.END, formatted_json + "\n", 'value')
        except json.JSONDecodeError as e:
            self.extended_detail_text.insert(tk.END, f"JSONの解析に失敗: {e}\n", 'error')

    def _show_timestamp_details(self, value: str):
        """
        Timestampdetails
        タイムスタンプの詳細表示
        """
        try:
            # 様々な形式での時刻表示
            formats = {
                "JST (日本時間)": "Asia/Tokyo",
                "UTC (世界協定時)": "UTC",
                "GMT (グリニッジ標準時)": "GMT",
                "US/Pacific (太平洋時間)": "US/Pacific",
                "US/Eastern (東部時間)": "US/Eastern",
                "Europe/London (英国時間)": "Europe/London",
                "Europe/Paris (中央ヨーロッパ時間)": "Europe/Paris",
                "Asia/Shanghai (中国時間)": "Asia/Shanghai",
                "Asia/Seoul (韓国時間)": "Asia/Seoul",
                "Australia/Sydney (シドニー時間)": "Australia/Sydney"
            }
            
            # UNIX時間での表示
            self.extended_detail_text.insert(tk.END, "=== UNIX時間表示 ===\n", 'header')
            try:
                unix_formats = {
                    "UNIX秒": "UNIX_second",
                    "UNIXミリ秒": "UNIX_millisecond",
                    "UNIXマイクロ秒": "UNIX_microsecond"
                }
                for label, fmt in unix_formats.items():
                    unix_time = convert_timestamp(value, fmt)
                    self.extended_detail_text.insert(tk.END, f"{label}:\n", 'field')
                    self.extended_detail_text.insert(tk.END, f"{unix_time}\n", 'value')
            except:
                pass

            # プラットフォーム固有の表示
            self.extended_detail_text.insert(tk.END, "\n=== プラットフォーム固有表示 ===\n", 'header')
            try:
                platform_formats = {
                    "Windows (FILETIME)": "FILETIME",
                    "Mac (HFS+)": "MAC",
                    "COCOA": "COCOA",
                    "WebKit": "WEBKIT",
                    "Chrome": "CHROME",
                    "Firefox": "FIREFOX"
                }
                for label, fmt in platform_formats.items():
                    platform_time = convert_timestamp(value, fmt)
                    self.extended_detail_text.insert(tk.END, f"{label}:\n", 'field')
                    self.extended_detail_text.insert(tk.END, f"{platform_time}\n", 'value')
            except:
                pass

            # タイムゾーン別の表示
            self.extended_detail_text.insert(tk.END, "\n=== タイムゾーン別表示 ===\n", 'header')
            for tz_name, tz in formats.items():
                try:
                    converted_time = convert_timestamp(value, tz)
                    self.extended_detail_text.insert(tk.END, f"{tz_name}:\n", 'field')
                    self.extended_detail_text.insert(tk.END, f"{converted_time}\n", 'value')
                except:
                    continue
                    
        except Exception as e:
            self.extended_detail_text.insert(tk.END, f"タイムスタンプの変換に失敗: {e}\n", 'error')

    def _show_text_details(self, value: str):
        """
        TextFileDetails
        テキストデータの詳細表示
        """
        self.extended_detail_text.insert(tk.END, "テキスト解析:\n", 'field')
        self.extended_detail_text.insert(tk.END, f"文字数: {len(value)}\n", 'info')
        self.extended_detail_text.insert(tk.END, f"行数: {value.count('\n') + 1}\n", 'info')
        if len(value) > 0:
            self.extended_detail_text.insert(tk.END, "\n文字種別:\n", 'field')
            if value.isascii():
                self.extended_detail_text.insert(tk.END, "ASCII文字のみ\n", 'info')
            else:
                self.extended_detail_text.insert(tk.END, "非ASCII文字を含む\n", 'info')

    def _apply_text_styles(self, text_widget):
        """
        ApplyTextWidgetStyles
        テキストウィジェットにスタイルを適用
        """
        # ヘッダー用スタイル（大見出し）
        text_widget.tag_configure('header', 
                                font=('Courier', 11, 'bold'), 
                                foreground='#0066cc',
                                spacing1=5,  # 段落前の空白
                                spacing3=5)  # 段落後の空白

        # フィールド名用スタイル（項目名）
        text_widget.tag_configure('field', 
                                font=('TkDefaultFont', 10, 'bold'),
                                spacing1=3)  # 項目前の空白

        # 値表示用スタイル（通常のテキスト）
        text_widget.tag_configure('value', 
                                font=('TkDefaultFont', 10),
                                spacing2=2)  # 行間の空白

        # 情報表示用スタイル（補足情報）
        text_widget.tag_configure('info', 
                                font=('TkDefaultFont', 10, 'italic'),
                                foreground='#666666')

        # NULL値表示用スタイル
        text_widget.tag_configure('null', 
                                font=('TkDefaultFont', 10),
                                foreground='gray',
                                spacing1=2)

        # エラー表示用スタイル
        text_widget.tag_configure('error', 
                                font=('TkDefaultFont', 10),
                                foreground='red',
                                spacing1=3)

        # バイナリ表示用のスタイル
        text_widget.tag_configure('offset', 
                                font=('Courier', 10),
                                foreground='#666666')
        
        text_widget.tag_configure('hex', 
                                font=('Courier', 10))
        
        text_widget.tag_configure('ascii', 
                                font=('Courier', 10),
                                foreground='#0066cc')
        
        text_widget.tag_configure('separator', 
                                font=('Courier', 10),
                                foreground='#999999')

    def _show_error_in_details(self, error_message: str):
        """
        ShowErrorInDetails
        エラーメッセージを全てのタブに表示
        """
        for text_widget in [self.detail_text, self.extended_detail_text, self.hex_detail_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert(tk.END, error_message, 'error')
            text_widget.config(state=tk.DISABLED)

    def on_tree_select(self, event):
        """ツリービューの選択イベント処理"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            if values:
                text = "\n".join(str(v) for v in values)
                self.update_result_text(text)

    def on_header_double_click(self, event):
        """
        ヘッダーダブルクリック時の処理
        """
        region = self.tree.identify('region', event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            column_name = self.tree["columns"][int(column[1]) - 1]
            
            if self.is_timestamp_column(column_name):
                menu = TimeFormatMenu(self, column_name, self._on_time_format_change)
                menu.post(event.x_root, event.y_root)

    def _on_time_format_change(self, column_name: str, format_type: str):
        """時間フォーマットの変更処理"""
        self.time_display_modes[column_name] = format_type
        self._refresh_tree_data()

    def _refresh_tree_data(self):
        """ツリービューのデータを更新"""
        for item in self.tree.get_children():
            values = list(self.tree.item(item)['values'])
            for i, col in enumerate(self.tree["columns"]):
                if self.is_timestamp_column(col):
                    values[i] = convert_timestamp(
                        values[i],
                        self.time_display_modes.get(col, "JST")
                    )
            self.tree.item(item, values=values)

    def _configure_tree_tags(self):
        """ツリービューのタグを設定"""
        self.tree.tag_configure('search_result', background='#fff3cd')  # 検索結果
        self.tree.tag_configure('selected_row', background='#cce5ff')   # 選択行
        self.tree.tag_configure('selected_cell', background='#e2e3e5')  # 選択セル
        self.tree.tag_configure('wal_record', foreground='red')         # WALレコード

    def is_timestamp_column(self, column_name: str) -> bool:
        """
        SearchTimestampColumn
        タイムスタンプカラムかどうかを判定
        """
        timestamp_keywords = [
            # 一般的なタイムスタンプキーワード
            'TIMESTAMP',
            'TIME',
            'DATE',
            # 作成・更新関連
            'CREATED',
            'MODIFIED',
            'UPDATED',
            'LAST_UPDATED',
            'LAST_MODIFIED',
            'CREATE_TIME',
            'UPDATE_TIME',
            'MOD_TIME',
            # LINE特有のプレフィックス
            'Z_TIMESTAMP',
            'ZLASTUPDATE',
            'ZLASTMODIFIED',
            'ZCREATEDAT',
            'ZUPDATEDAT',
            # その他の一般的な表現
            'DATETIME',
            'POSTED_AT',
            'SENT_AT',
            'RECEIVED_AT',
            'DELIVERED_AT',
            'READ_AT',
            'ACCESSED_AT',
            'LOGGED_AT',
            # 日付関連
            'BIRTH',
            'DEATH',
            'START',
            'END',
            'EXPIRE',
            'DEADLINE'
        ]
        return any(keyword in column_name.upper() for keyword in timestamp_keywords)

    def _perform_search(self):
        """検索を実行"""
        search_text = self.search_var.get()
        if not search_text:
            self._clear_search()
            return

        # 以前の検索結果をクリア
        self._clear_search_highlights()

        # 検索条件を取得
        case_sensitive = self.case_sensitive_var.get()
        include_null = self.include_null_var.get()
        search_column = self.search_column_var.get()
        search_condition = self.search_condition_var.get()

        if not case_sensitive:
            search_text = search_text.lower()

        # 検索実行
        matches = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            
            # 検索対象のカラムを決定
            if search_column == "すべて":
                columns_to_search = range(len(values))
            else:
                try:
                    col_idx = self.tree["columns"].index(search_column)
                    columns_to_search = [col_idx]
                except ValueError:
                    continue

            # 各カラムで検索
            for col_idx in columns_to_search:
                value = values[col_idx]
                
                # NULL値の処理
                if value is None:
                    if include_null:
                        matches.append(item)
                    continue

                str_value = str(value)
                if not case_sensitive:
                    str_value = str_value.lower()

                # 検索条件に応じた比較
                match = False
                if search_condition == "完全一致":
                    match = str_value == search_text
                elif search_condition == "前方一致":
                    match = str_value.startswith(search_text)
                elif search_condition == "後方一致":
                    match = str_value.endswith(search_text)
                else:  # 含む
                    match = search_text in str_value

                if match:
                    matches.append(item)
                    break

        # 検索結果をハイライト
        for item in matches:
            current_tags = list(self.tree.item(item).get('tags', []))
            if 'search_result' not in current_tags:
                current_tags.append('search_result')
            self.tree.item(item, tags=current_tags)
        
        # 検索結果数を更新
        match_count = len(matches)
        if match_count > 0:
            self.search_count_label.config(
                text=f"検索結果: {match_count}件"
            )
            # 最初の検索結果にスクロール
            self.tree.see(matches[0])
        else:
            self.search_count_label.config(text="検索結果: 0件")

    def _clear_search(self):
        """検索をクリア"""
        self.search_var.set("")
        self._clear_search_highlights()
        self.search_count_label.config(text="")

    def _clear_search_highlights(self):
        """検索結果のハイライトをクリア"""
        for item in self.tree.get_children():
            current_tags = list(self.tree.item(item).get('tags', []))
            if 'search_result' in current_tags:
                current_tags.remove('search_result')
            self.tree.item(item, tags=current_tags)

    def _calculate_column_widths(self, columns: List[str], data: List[tuple]) -> Dict[str, int]:
        """カラム幅を計算

        Args:
            columns (List[str]): カラム名のリスト
            data (List[tuple]): テーブルデータ

        Returns:
            Dict[str, int]: カラムごとの推奨幅（ピクセル単位）
        """
        # 定数定義
        MIN_WIDTH = 50      # 最小幅（ピクセル）
        MAX_WIDTH = 300     # 最大幅（ピクセル）
        CHAR_WIDTH = 7      # 文字あたりの平均幅（ピクセル）
        TIMESTAMP_WIDTH = 180  # タイムスタンプ用の固定幅
        
        # カラム幅の初期化（カラム名の長さを基準）
        col_widths = {col: len(str(col)) for col in columns}
        
        try:
            # サンプリングするデータ数を制限（パフォーマンス向上のため）
            sample_size = min(1000, len(data))
            sample_data = data[:sample_size]
            
            # データからカラム幅を計算
            for row in sample_data:
                for i, value in enumerate(row):
                    col = columns[i]
                    if value is not None:
                        str_value = str(value)
                        
                        # カラムタイプに応じた処理
                        if self.is_timestamp_column(col):
                            # タイムスタンプは固定幅を使用
                            col_widths[col] = TIMESTAMP_WIDTH
                        elif len(str_value) > 100:
                            # 長いテキストは最大幅を使用
                            col_widths[col] = MAX_WIDTH
                        else:
                            # 通常のデータは内容に応じて調整
                            col_widths[col] = max(
                                col_widths[col],
                                min(len(str_value), MAX_WIDTH // CHAR_WIDTH)
                            )
            
            # ピクセル単位に変換して返却
            return {
                col: min(max(width * CHAR_WIDTH, MIN_WIDTH), MAX_WIDTH)
                for col, width in col_widths.items()
            }
            
        except Exception as e:
            print(f"カラム幅の計算エラー: {e}")
            # エラー時はデフォルト値を返却
            return {col: 150 for col in columns}

    def on_table_select(self, event):
        """テーブル選択時の処理"""
        table_name = self.get_selected_table(clear_display=False)
        if not table_name:
            return

        try:
            # オリジナル値キャッシュをクリア
            self.original_values_cache.clear()
            
            # プログレスバーを表示
            progress_window = tk.Toplevel(self)
            progress_window.title("Loading Table Data...")
            progress_window.geometry("400x80")
            progress_window.transient(self)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text="テーブルデータを読み込み中...")
            progress_label.pack(pady=(10,5))
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(fill=tk.X, padx=20, pady=5)
            progress_bar.start(10)
            progress_window.update()

            # テーブルの行数を取得
            total_rows = get_table_row_count(self.cursor, table_name)
            
            # 閾値を設定（例：10000行）
            THRESHOLD = 10000
            
            # 大きなテーブルの場合は警告を表示
            if total_rows > THRESHOLD:
                progress_window.destroy()
                response = messagebox.askquestion(
                    "表示行数の選択",
                    f"このテーブルには{total_rows:,}行のデータがあります。\n"
                    f"どちらの表示方法を選択しますか？\n\n"
                    f"「はい」: すべての{total_rows:,}行を表示\n"
                    f"「いいえ」: 最初の{THRESHOLD:,}行のみ表示",
                    icon='question'
                )
                limit = None if response == 'yes' else THRESHOLD
                
                # プログレスバーを再表示
                progress_window = tk.Toplevel(self)
                progress_window.title("Loading Table Data...")
                progress_window.geometry("400x80")
                progress_window.transient(self)
                progress_window.grab_set()
                
                progress_label = ttk.Label(progress_window, text="テーブルデータを読み込み中...")
                progress_label.pack(pady=(10,5))
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(fill=tk.X, padx=20, pady=5)
                progress_bar.start(10)
                progress_window.update()
            else:
                limit = None  # 小さなテーブルは全て表示

            # テーブルの内容をWALデータと共に取得
            columns, data, wal_records = get_table_contents_with_wal(
                self.cursor, 
                table_name, 
                self.current_db_path,
                limit=limit
            )
            self.wal_records = wal_records  # WALレコードを保存
            
            if not columns or not data:
                progress_window.destroy()
                return

            # ツリービューをクリア
            for item in self.tree.get_children():
                self.tree.delete(item)

            # カラムを設定
            self.tree["columns"] = columns
            self.tree["show"] = "headings"

            # 検索用のカラムコンボボックスを更新
            self.column_combo['values'] = ["すべて"] + list(columns)
            self.column_combo.set("すべて")

            # カラム幅を計算
            col_widths = self._calculate_column_widths(columns, data)

            # カラムの設定
            for col in columns:
                self.tree.heading(col, 
                                text=col,
                                anchor=tk.CENTER)
                
                self.tree.column(col,
                               width=col_widths[col],
                               minwidth=80,
                               stretch=True,
                               anchor=tk.W)
                
                if self.is_timestamp_column(col):
                    self.tree.heading(col, text=f"{col} 🕒")
                    self.tree.heading(col, command=lambda c=col: self._show_time_format_menu(c))

            # グリッド線の表示設定を更新
            self.tree.tag_configure('evenrow', background='#f0f0f0')
            self.tree.tag_configure('oddrow', background='white')

            # データを効率的に追加
            progress_label.config(text="データを表示中...")
            progress_window.update()
            
            batch_size = 100  # バッチサイズを設定
            for batch_start in range(0, len(data), batch_size):
                batch_end = min(batch_start + batch_size, len(data))
                batch_data = data[batch_start:batch_end]
                
                for i, row in enumerate(batch_data):
                    actual_index = batch_start + i
                    converted_row = list(row)
                    timestamp_columns = {}
                    
                    # タイムスタンプカラムを効率的に処理
                    for j, col in enumerate(columns):
                        if self.is_timestamp_column(col) and converted_row[j] is not None:
                            try:
                                # 元の値を保存
                                timestamp_columns[j] = str(converted_row[j])
                                # 値を変換
                                converted_row[j] = convert_timestamp(converted_row[j], "JST")
                            except Exception:
                                pass  # 変換に失敗した場合は元の値のまま
                    
                    # 行の背景色を設定
                    row_tags = ['evenrow' if actual_index % 2 == 0 else 'oddrow']
                    
                    # WALレコードのチェック
                    if actual_index in self.wal_records:
                        row_tags.append('wal_record')
                    
                    # 行を挿入
                    item = self.tree.insert("", tk.END, values=converted_row, tags=row_tags)
                    
                    # オリジナル値をキャッシュに保存
                    if timestamp_columns:
                        self.original_values_cache[item] = timestamp_columns
                
                # UIを更新（レスポンシブにするため）
                if batch_start % (batch_size * 5) == 0:  # 5バッチごとに更新
                    progress_window.update()

            progress_window.destroy()

            # ステータス表示を更新
            status_text = f"表示中: {len(data):,} 行 (WALデータ: {len(self.wal_records):,} 行)"
            if limit and total_rows > limit:
                status_text += f" / 全{total_rows:,}行"
            self.update_status(status_text)

            # テーブル情報を表示
            self.analyze_table()

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            messagebox.showerror("エラー", f"テーブル内容の読み込みエラー: {e}")

    def _show_time_format_menu(self, column_name: str):
        """
        ShoeTimestampMenu
        タイムスタンプの表示形式メニューを表示
        """
        menu = TimeFormatMenu(self, column_name, self._on_time_format_change)
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def update_status(self, text: str):
        """
        UpdateStutesbar
        ステータスバーを更新
        """
        if not hasattr(self, 'status_label'):
            self.status_label = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
            self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label.config(text=text)

    def __del__(self):
        """
        Destructor:Closeddatebaseconnection
        デストラクタ：データベース接続を閉じる
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def _update_hex_detail(self, value: Any, data_type: str):
        """
        UpdateHEXDetails
        HEX表示タブの更新
        """
        self.hex_detail_text.config(state=tk.NORMAL)
        self.hex_detail_text.delete('1.0', tk.END)

        try:
            # データをバイト列に変換
            if isinstance(value, (bytes, bytearray)):
                byte_data = value
            elif isinstance(value, str):
                byte_data = value.encode('utf-8')
            elif value is None:
                byte_data = b'NULL'
            else:
                byte_data = str(value).encode('utf-8')

            # サイズ情報を表示
            self.hex_detail_text.insert(tk.END, f"データサイズ: {len(byte_data)} bytes\n\n", 'info')

            # ヘッダー行を追加
            self.hex_detail_text.insert(tk.END, "Address     ", 'header')
            self.hex_detail_text.insert(tk.END, "│ ", 'separator')
            
            # 16進数のヘッダーを作成
            hex_header = ""
            for i in range(16):
                if i == 8:
                    hex_header += " "
                hex_header += f"{i:02X}"
                if i < 15:
                    hex_header += " "
            
            self.hex_detail_text.insert(tk.END, hex_header, 'header')
            self.hex_detail_text.insert(tk.END, " │ ", 'separator')
            self.hex_detail_text.insert(tk.END, "ASCII\n", 'header')

            # 区切り線
            self.hex_detail_text.insert(tk.END, "─" * 10, 'separator')
            self.hex_detail_text.insert(tk.END, "┼", 'separator')
            self.hex_detail_text.insert(tk.END, "─" * 48, 'separator')
            self.hex_detail_text.insert(tk.END, "┼", 'separator')
            self.hex_detail_text.insert(tk.END, "─" * 16, 'separator')
            self.hex_detail_text.insert(tk.END, "\n")

            # 16進数ダンプとASCII表示を生成（全データを表示）
            BYTES_PER_LINE = 16
            offset = 0
            
            while offset < len(byte_data):
                # オフセットを表示
                self.hex_detail_text.insert(tk.END, f"{offset:08X}", 'offset')
                self.hex_detail_text.insert(tk.END, " │ ", 'separator')
                
                chunk = byte_data[offset:offset + BYTES_PER_LINE]
                hex_values = []
                ascii_values = []
                
                # 16進数とASCII文字を生成
                for i, byte in enumerate(chunk):
                    hex_values.append(f"{byte:02X}")
                    ascii_values.append(chr(byte) if 32 <= byte <= 126 else '.')
                    
                    if i == 7:
                        hex_values.append('')
                
                # 16進数部分の表示（不足分はスペースで埋める）
                hex_line = ' '.join(hex_values)
                hex_line = hex_line.ljust(47)
                self.hex_detail_text.insert(tk.END, hex_line, 'hex')
                self.hex_detail_text.insert(tk.END, " │ ", 'separator')
                
                # ASCII部分の表示
                ascii_line = ''.join(ascii_values).ljust(16)
                self.hex_detail_text.insert(tk.END, ascii_line, 'ascii')
                self.hex_detail_text.insert(tk.END, "\n")
                
                offset += BYTES_PER_LINE

        except Exception as e:
            self.hex_detail_text.insert(tk.END, f"ShowHEXError/HEX表示エラー: {e}\n", 'error')

        self._apply_text_styles(self.hex_detail_text)
        self.hex_detail_text.config(state=tk.DISABLED)

    def _detect_image_from_hex(self, data: bytes) -> Optional[Tuple[str, bytes]]:
        """
        ExtractImagefromHex
        HEXデータから画像を検出
        
        Returns:
            Optional[Tuple[str, bytes]]: (image_type, image_data) or None
        """
        # 主要な画像形式のマジックナンバー
        IMAGE_SIGNATURES = {
            b'\xE0\xDD\xD8\xFF': 'JPEG',
            b'\x61\x39\x38\x46\x49\x47': 'GIF(GIF89a)',
            b'\x61\x37\x38\x46\x49\x47': 'GIF(GIF87a)',
            b'\x0A\x1A\x0A\x0D\x47\x4E\x50\x89': 'PNG',
            b'BM': 'BMP',
            b'\x00\x00\x01\x00': 'ICO',
            b'II*\x00': 'TIFF',
            b'MM\x00*': 'TIFF',
            b'\x53\x50\x42\x38': 'PSD',
            b'\x46\x46\x49\x52': 'Webp'
        }
        
        # データがバイト列でない場合は変換（完全なデータを保持）
        if not isinstance(data, bytes):
            try:
                if isinstance(data, str):
                    # 16進文字列の場合
                    if all(c in '0123456789ABCDEFabcdef' for c in data.replace(' ', '')):
                        data = bytes.fromhex(data.replace(' ', ''))
                    else:
                        data = data.encode('utf-8')
                else:
                    data = str(data).encode('utf-8')
            except:
                return None
        
        # 画像シグネチャの検索（完全なデータを返す）
        for signature, image_type in IMAGE_SIGNATURES.items():
            if data.startswith(signature):
                return image_type, data
            
            # データ内の任意の位置で画像を検索
            pos = data.find(signature)
            if pos >= 0:
                # 見つかった位置から末尾までの完全なデータを返す
                return image_type, data[pos:]
        
        return None

    def _toggle_image_display(self):
        """
        ToggleImageDisplay
        画像の表示モードを切り替え
        """
        self.show_full_image_var.set(not self.show_full_image_var.get())
        if hasattr(self, 'current_image_data'):
            self._update_image_preview(self.current_image_data, force_update=True)
        
        # ボタンのテキストを更新
        if self.show_full_image_var.get():
            self.toggle_image_button.config(text="Abbreviation/省略表示")
        else:
            self.toggle_image_button.config(text="ShowAll/全て表示")

    def _update_image_preview(self, value: Any, force_update: bool = False):
        """
        UpdateImageView
        画像プレビュータブの更新
        """
        self.image_canvas.delete('all')
        self.image_info_label.config(text="")
        
        try:
            # 現在のデータを保存
            self.current_image_data = value
            
            # 画像データの検出
            image_info = self._detect_image_from_hex(value)
            if not image_info:
                self.image_info_label.config(text="NothingImage/画像データが検出できません。")
                return
            
            image_type, image_data = image_info
            
            # 画像の読み込みと表示
            image = Image.open(io.BytesIO(image_data))
            
            # キャンバスのサイズを取得
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:  # キャンバスがまだ正しいサイズを持っていない場合
                canvas_width = 300
                canvas_height = 300
            
            if self.show_full_image_var.get():
                # フルサイズ表示モード
                # スクロール可能な大きさに制限
                max_size = (800, 600)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            else:
                # 省略表示モード
                # キャンバスサイズに合わせる
                image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            # PhotoImageに変換
            photo = ImageTk.PhotoImage(image)
            
            # キャンバスのサイズを更新（必要な場合）
            if self.show_full_image_var.get():
                self.image_canvas.config(
                    width=max(canvas_width, photo.width()),
                    height=max(canvas_height, photo.height())
                )
            
            # 画像をキャンバスの中央に配置
            x = (self.image_canvas.winfo_width() - photo.width()) // 2
            y = (self.image_canvas.winfo_height() - photo.height()) // 2
            
            # 画像の表示
            self.image_canvas.create_image(x, y, image=photo, anchor=tk.NW)
            self.image_canvas.image = photo  # 参照を保持
            
            # 画像情報の表示
            info_text = f"ImageType/画像タイプ: {image_type}\n"
            info_text += f"Size/サイズ: {image.size[0]}x{image.size[1]} px\n"
            info_text += f"Mode/モード: {image.mode}"
            self.image_info_label.config(text=info_text)
            
        except Exception as e:
            self.image_info_label.config(text=f"ShowImageError/画像の表示に失敗しました: {e}")

if __name__ == "__main__":
    app = LineDBViewer()
    app.mainloop() 