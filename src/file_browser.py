"""
ファイル・フォルダブラウザーモジュール
ローカルファイルシステムからPythonファイルを選択する機能を提供
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import ipywidgets as widgets
from IPython.display import display


@dataclass
class FileInfo:
    """ファイル情報データクラス"""
    path: str
    name: str
    size: int
    is_directory: bool
    extension: str
    modified_time: float


class FileBrowser:
    """ファイルブラウザークラス"""
    
    SUPPORTED_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.rb', '.php']
    
    def __init__(self, start_path: str = None):
        """
        初期化
        
        Args:
            start_path (str): 開始ディレクトリパス
        """
        self.start_path = start_path or os.getcwd()
        self.current_path = self.start_path
        self.selected_files = []
        self.selected_folders = []
        
        # UI コンポーネント
        self.path_label = None
        self.file_list = None
        self.selection_list = None
        self.controls = None
        
    def get_directory_contents(self, path: str = None) -> List[FileInfo]:
        """
        ディレクトリの内容を取得
        
        Args:
            path (str): ディレクトリパス
            
        Returns:
            List[FileInfo]: ファイル・フォルダのリスト
        """
        target_path = path or self.current_path
        contents = []
        
        try:
            # 親ディレクトリへのリンク
            if target_path != '/':
                parent_path = str(Path(target_path).parent)
                contents.append(FileInfo(
                    path=parent_path,
                    name='.. (親ディレクトリ)',
                    size=0,
                    is_directory=True,
                    extension='',
                    modified_time=0
                ))
            
            # ディレクトリ内のアイテムを取得
            for item_path in sorted(Path(target_path).iterdir()):
                if item_path.name.startswith('.'):
                    continue  # 隠しファイル・フォルダをスキップ
                    
                try:
                    stat = item_path.stat()
                    info = FileInfo(
                        path=str(item_path),
                        name=item_path.name,
                        size=stat.st_size if item_path.is_file() else 0,
                        is_directory=item_path.is_dir(),
                        extension=item_path.suffix.lower() if item_path.is_file() else '',
                        modified_time=stat.st_mtime
                    )
                    contents.append(info)
                except (PermissionError, OSError):
                    continue  # アクセス権限がない場合はスキップ
                    
        except (PermissionError, OSError):
            pass  # ディレクトリにアクセスできない場合
            
        return contents
    
    def find_python_files(self, directory: str = None, recursive: bool = True) -> List[str]:
        """
        指定ディレクトリからPythonファイルを検索
        
        Args:
            directory (str): 検索ディレクトリ
            recursive (bool): 再帰的に検索するか
            
        Returns:
            List[str]: Pythonファイルのパスリスト
        """
        search_dir = directory or self.current_path
        
        if recursive:
            pattern = os.path.join(search_dir, '**', '*.py')
            return glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(search_dir, '*.py')
            return glob.glob(pattern)
    
    def find_code_files(self, directory: str = None, extensions: List[str] = None) -> Dict[str, List[str]]:
        """
        指定した拡張子のコードファイルを検索
        
        Args:
            directory (str): 検索ディレクトリ
            extensions (List[str]): 検索する拡張子のリスト
            
        Returns:
            Dict[str, List[str]]: 拡張子別のファイルパスリスト
        """
        search_dir = directory or self.current_path
        target_extensions = extensions or self.SUPPORTED_EXTENSIONS
        
        results = {}
        for ext in target_extensions:
            pattern = os.path.join(search_dir, '**', f'*{ext}')
            files = glob.glob(pattern, recursive=True)
            if files:
                results[ext] = files
                
        return results
    
    def create_file_browser_ui(self) -> widgets.VBox:
        """
        ファイルブラウザーUIを作成
        
        Returns:
            widgets.VBox: ファイルブラウザーUI
        """
        # パス表示
        self.path_label = widgets.HTML(
            value=f"<b>現在のパス:</b> {self.current_path}",
            layout={'margin': '0 0 10px 0'}
        )
        
        # ファイルリスト
        contents = self.get_directory_contents()
        file_options = []
        
        for item in contents:
            icon = "📁" if item.is_directory else self._get_file_icon(item.extension)
            size_str = self._format_size(item.size) if not item.is_directory else ""
            display_name = f"{icon} {item.name} {size_str}".strip()
            file_options.append((display_name, item.path))
        
        self.file_list = widgets.Select(
            options=file_options,
            description='ファイル:',
            layout={'height': '300px', 'width': '100%'}
        )
        
        # 選択されたファイル・フォルダのリスト
        self.selection_list = widgets.Textarea(
            description='選択済み:',
            placeholder='選択したファイルがここに表示されます',
            layout={'height': '120px', 'width': '100%'}
        )
        
        # ボタン
        navigate_btn = widgets.Button(
            description='移動',
            button_style='info',
            icon='folder-open'
        )
        
        select_file_btn = widgets.Button(
            description='ファイル選択',
            button_style='success',
            icon='file'
        )
        
        select_folder_btn = widgets.Button(
            description='フォルダ選択',
            button_style='warning',
            icon='folder'
        )
        
        clear_btn = widgets.Button(
            description='クリア',
            button_style='danger',
            icon='trash'
        )
        
        # イベントハンドラー
        navigate_btn.on_click(self._on_navigate_click)
        select_file_btn.on_click(self._on_select_file_click)
        select_folder_btn.on_click(self._on_select_folder_click)
        clear_btn.on_click(self._on_clear_click)
        
        # レイアウト
        button_box = widgets.HBox([
            navigate_btn, select_file_btn, select_folder_btn, clear_btn
        ])
        
        self.controls = widgets.VBox([
            self.path_label,
            self.file_list,
            button_box,
            self.selection_list
        ])
        
        return self.controls
    
    def _get_file_icon(self, extension: str) -> str:
        """ファイル拡張子に応じたアイコンを返す"""
        icon_map = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.java': '☕',
            '.go': '🐹',
            '.rs': '🦀',
            '.cpp': '⚙️',
            '.c': '⚙️',
            '.rb': '💎',
            '.php': '🐘',
            '.md': '📝',
            '.txt': '📄',
            '.json': '📋',
            '.yml': '⚙️',
            '.yaml': '⚙️'
        }
        return icon_map.get(extension, '📄')
    
    def _format_size(self, size: int) -> str:
        """ファイルサイズをフォーマット"""
        if size < 1024:
            return f"({size}B)"
        elif size < 1024 * 1024:
            return f"({size/1024:.1f}KB)"
        else:
            return f"({size/(1024*1024):.1f}MB)"
    
    def _on_navigate_click(self, button):
        """移動ボタンのクリックハンドラー"""
        if self.file_list.value:
            selected_path = self.file_list.value
            if os.path.isdir(selected_path):
                self.current_path = selected_path
                self._refresh_file_list()
    
    def _on_select_file_click(self, button):
        """ファイル選択ボタンのクリックハンドラー"""
        if self.file_list.value:
            selected_path = self.file_list.value
            if os.path.isfile(selected_path) and selected_path not in self.selected_files:
                self.selected_files.append(selected_path)
                self._update_selection_display()
    
    def _on_select_folder_click(self, button):
        """フォルダ選択ボタンのクリックハンドラー"""
        if self.file_list.value:
            selected_path = self.file_list.value
            if os.path.isdir(selected_path) and selected_path not in self.selected_folders:
                self.selected_folders.append(selected_path)
                self._update_selection_display()
    
    def _on_clear_click(self, button):
        """クリアボタンのクリックハンドラー"""
        self.selected_files = []
        self.selected_folders = []
        self._update_selection_display()
    
    def _refresh_file_list(self):
        """ファイルリストを更新"""
        self.path_label.value = f"<b>現在のパス:</b> {self.current_path}"
        
        contents = self.get_directory_contents()
        file_options = []
        
        for item in contents:
            icon = "📁" if item.is_directory else self._get_file_icon(item.extension)
            size_str = self._format_size(item.size) if not item.is_directory else ""
            display_name = f"{icon} {item.name} {size_str}".strip()
            file_options.append((display_name, item.path))
        
        self.file_list.options = file_options
    
    def _update_selection_display(self):
        """選択表示を更新"""
        lines = []
        
        if self.selected_files:
            lines.append("📄 選択ファイル:")
            for file_path in self.selected_files:
                lines.append(f"  • {file_path}")
        
        if self.selected_folders:
            lines.append("📁 選択フォルダ:")
            for folder_path in self.selected_folders:
                lines.append(f"  • {folder_path}")
        
        if not lines:
            lines.append("選択されたファイル・フォルダはありません")
        
        self.selection_list.value = '\n'.join(lines)
    
    def get_selected_files(self) -> List[str]:
        """選択されたファイルのリストを取得"""
        all_files = self.selected_files.copy()
        
        # 選択されたフォルダ内のファイルも含める
        for folder in self.selected_folders:
            code_files = self.find_code_files(folder)
            for ext, files in code_files.items():
                all_files.extend(files)
        
        # 重複を削除
        return list(set(all_files))
    
    def read_selected_files(self) -> Dict[str, str]:
        """
        選択されたファイルの内容を読み取り
        
        Returns:
            Dict[str, str]: ファイルパス -> ファイル内容のマッピング
        """
        file_contents = {}
        selected_files = self.get_selected_files()
        
        for file_path in selected_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents[file_path] = f.read()
            except Exception as e:
                file_contents[file_path] = f"# エラー: ファイルを読み込めませんでした: {str(e)}"
        
        return file_contents
    
    def create_quick_select_widget(self, extensions: List[str] = None) -> widgets.VBox:
        """
        クイック選択ウィジェットを作成（現在のディレクトリから指定拡張子のファイルを自動検索）
        
        Args:
            extensions (List[str]): 検索する拡張子のリスト
            
        Returns:
            widgets.VBox: クイック選択UI
        """
        target_extensions = extensions or ['.py']
        
        # ファイルを検索
        found_files = {}
        for ext in target_extensions:
            pattern = os.path.join(self.current_path, '**', f'*{ext}')
            files = glob.glob(pattern, recursive=True)
            if files:
                found_files[ext] = files
        
        # チェックボックスで選択
        file_checkboxes = []
        for ext, files in found_files.items():
            ext_label = widgets.HTML(f"<b>{ext} ファイル ({len(files)}個):</b>")
            file_checkboxes.append(ext_label)
            
            for file_path in files[:10]:  # 最初の10個まで表示
                checkbox = widgets.Checkbox(
                    value=False,
                    description=os.path.relpath(file_path, self.current_path),
                    layout={'margin': '0 0 0 20px'}
                )
                checkbox.file_path = file_path  # ファイルパスを保存
                file_checkboxes.append(checkbox)
        
        select_all_btn = widgets.Button(
            description='すべて選択',
            button_style='info',
            icon='check-square'
        )
        
        def on_select_all(b):
            for widget in file_checkboxes:
                if hasattr(widget, 'value'):
                    widget.value = True
        
        select_all_btn.on_click(on_select_all)
        
        return widgets.VBox([select_all_btn] + file_checkboxes)
    
    def get_selected_from_checkboxes(self, checkbox_container: widgets.VBox) -> List[str]:
        """チェックボックスから選択されたファイルのリストを取得"""
        selected = []
        for widget in checkbox_container.children:
            if hasattr(widget, 'value') and hasattr(widget, 'file_path') and widget.value:
                selected.append(widget.file_path)
        return selected