"""
コード入力処理モジュール
PoCデモプログラムのソースコードを受け取り、プロンプト生成に活用
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import ast
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from collections import Counter


@dataclass
class CodeInput:
    """コード入力データクラス"""
    code: str
    language: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    timestamp: Optional[str] = None

@dataclass
class FileCodeInput:
    """ファイルから読み込んだコード入力データクラス"""
    file_path: str
    code: str
    language: Optional[str] = None
    file_size: int = 0
    modified_time: Optional[str] = None
    relative_path: Optional[str] = None


@dataclass
class MultiFileInput:
    """複数ファイルの入力データクラス"""
    files: List[FileCodeInput]
    total_files: int = 0
    total_lines: int = 0
    project_root: Optional[str] = None
    description: Optional[str] = None
    

@dataclass
class CodeAnalysisResult:
    """コード解析結果データクラス"""
    language: str
    lines_of_code: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity_estimate: str  # simple, moderate, complex
    main_purpose: str
    suggested_improvements: List[str]
    

class CodeInputHandler:
    """コード入力処理クラス"""
    
    # サポート言語マッピング
    SUPPORTED_LANGUAGES = {
        'python': ['py', 'python', 'python3'],
        'javascript': ['js', 'javascript', 'jsx', 'node'],
        'typescript': ['ts', 'typescript', 'tsx'],
        'java': ['java'],
        'csharp': ['cs', 'csharp', 'c#'],
        'go': ['go', 'golang'],
        'rust': ['rs', 'rust'],
        'cpp': ['cpp', 'c++', 'cc'],
        'ruby': ['rb', 'ruby'],
        'php': ['php'],
        'swift': ['swift'],
        'kotlin': ['kt', 'kotlin']
    }
    
    def __init__(self):
        """初期化"""
        self.current_input = None
        self.analysis_result = None
        
    def detect_language(self, code: str, hint: Optional[str] = None) -> str:
        """
        コードの言語を自動判定
        
        Args:
            code (str): ソースコード
            hint (Optional[str]): 言語のヒント
            
        Returns:
            str: 判定された言語
        """
        if hint:
            # ヒントから言語を特定
            for lang, aliases in self.SUPPORTED_LANGUAGES.items():
                if hint.lower() in aliases:
                    return lang
        
        # パターンマッチングによる判定
        patterns = {
            'python': [
                r'^\s*def\s+\w+\s*\(', 
                r'^\s*class\s+\w+',
                r'^\s*import\s+\w+',
                r'^\s*from\s+\w+\s+import',
                r'^\s*if\s+__name__\s*==\s*["\']__main__["\']'
            ],
            'javascript': [
                r'^\s*function\s+\w+\s*\(',
                r'^\s*const\s+\w+\s*=',
                r'^\s*let\s+\w+\s*=',
                r'^\s*var\s+\w+\s*=',
                r'=>',
                r'console\.log\('
            ],
            'java': [
                r'^\s*public\s+class\s+\w+',
                r'^\s*private\s+\w+\s+\w+',
                r'^\s*public\s+static\s+void\s+main',
                r'System\.out\.println\('
            ],
            'typescript': [
                r'^\s*interface\s+\w+',
                r'^\s*type\s+\w+\s*=',
                r':\s*(string|number|boolean|any)\s*[;,\)]',
                r'^\s*export\s+(class|interface|type)'
            ]
        }
        
        # 各言語のパターンをチェック
        scores = {}
        for lang, lang_patterns in patterns.items():
            score = 0
            for pattern in lang_patterns:
                if re.search(pattern, code, re.MULTILINE):
                    score += 1
            scores[lang] = score
        
        # 最高スコアの言語を返す
        if scores:
            detected = max(scores, key=scores.get)
            if scores[detected] > 0:
                return detected
        
        # pygmentsのレクサーで判定
        try:
            lexer = guess_lexer(code)
            lexer_name = lexer.name.lower()
            for lang, aliases in self.SUPPORTED_LANGUAGES.items():
                if any(alias in lexer_name for alias in aliases):
                    return lang
        except:
            pass
        
        return 'unknown'
    
    def analyze_code(self, code: str, language: str) -> CodeAnalysisResult:
        """
        コードを解析
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            
        Returns:
            CodeAnalysisResult: 解析結果
        """
        lines = code.strip().split('\n')
        lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        functions = []
        classes = []
        imports = []
        
        if language == 'python':
            # Python固有の解析
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
            except:
                # AST解析失敗時は正規表現で簡易解析
                functions = re.findall(r'def\s+(\w+)\s*\(', code)
                classes = re.findall(r'class\s+(\w+)', code)
                imports = re.findall(r'import\s+([\w\.]+)', code)
        
        elif language == 'javascript' or language == 'typescript':
            # JavaScript/TypeScript解析
            functions = re.findall(r'function\s+(\w+)\s*\(', code)
            functions.extend(re.findall(r'const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=]+)\s*=>', code))
            classes = re.findall(r'class\s+(\w+)', code)
            imports = re.findall(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', code)
            
        elif language == 'java':
            # Java解析
            functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\(', code)
            classes = re.findall(r'(?:public\s+)?class\s+(\w+)', code)
            imports = re.findall(r'import\s+([\w\.]+);', code)
        
        # 複雑度の推定
        if lines_of_code < 50:
            complexity = 'simple'
        elif lines_of_code < 200:
            complexity = 'moderate'
        else:
            complexity = 'complex'
        
        # メイン目的の推定
        main_purpose = self._estimate_purpose(code, functions, classes, imports)
        
        # 改善提案の生成
        suggestions = self._generate_suggestions(code, language, complexity)
        
        return CodeAnalysisResult(
            language=language,
            lines_of_code=lines_of_code,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_estimate=complexity,
            main_purpose=main_purpose,
            suggested_improvements=suggestions
        )
    
    def _estimate_purpose(self, code: str, functions: List[str], 
                         classes: List[str], imports: List[str]) -> str:
        """コードの主要目的を推定"""
        code_lower = code.lower()
        
        # パターンベースの推定
        if any(imp for imp in imports if 'flask' in imp or 'fastapi' in imp or 'django' in imp):
            return "Web API/アプリケーション開発"
        elif any(imp for imp in imports if 'pandas' in imp or 'numpy' in imp):
            return "データ処理・分析"
        elif any(imp for imp in imports if 'tensorflow' in imp or 'torch' in imp or 'sklearn' in imp):
            return "機械学習モデル"
        elif 'test' in code_lower or 'assert' in code_lower:
            return "テストコード"
        elif any(cls for cls in classes if 'model' in cls.lower() or 'schema' in cls.lower()):
            return "データモデル定義"
        elif 'main' in functions or '__main__' in code:
            return "メインアプリケーション"
        else:
            return "ユーティリティ/ヘルパー機能"
    
    def _generate_suggestions(self, code: str, language: str, complexity: str) -> List[str]:
        """改善提案を生成"""
        suggestions = []
        
        # 共通の提案
        if '# TODO' in code or '// TODO' in code:
            suggestions.append("TODOコメントの解決")
        
        if complexity == 'complex':
            suggestions.append("関数の分割を検討（単一責任原則）")
        
        # 言語固有の提案
        if language == 'python':
            if 'except:' in code or 'except Exception:' in code:
                suggestions.append("具体的な例外タイプの指定")
            if not re.search(r'""".*?"""', code, re.DOTALL):
                suggestions.append("docstringの追加")
            if 'print(' in code:
                suggestions.append("loggingモジュールの使用を検討")
                
        elif language in ['javascript', 'typescript']:
            if 'var ' in code:
                suggestions.append("varをconst/letに置換")
            if 'console.log' in code:
                suggestions.append("本番環境用のログ機能実装")
            if language == 'javascript' and not 'use strict' in code:
                suggestions.append("'use strict'の追加")
        
        return suggestions
    
    def process_code_input(self, 
                          code: str, 
                          language: Optional[str] = None,
                          title: Optional[str] = None,
                          description: Optional[str] = None,
                          requirements: Optional[str] = None) -> Tuple[CodeInput, CodeAnalysisResult]:
        """
        コード入力を処理
        
        Args:
            code (str): ソースコード
            language (Optional[str]): プログラミング言語
            title (Optional[str]): コードのタイトル
            description (Optional[str]): コードの説明
            requirements (Optional[str]): 要件
            
        Returns:
            Tuple[CodeInput, CodeAnalysisResult]: 入力データと解析結果
        """
        # 言語判定
        detected_language = self.detect_language(code, language)
        
        # 入力データ作成
        self.current_input = CodeInput(
            code=code,
            language=detected_language,
            title=title,
            description=description,
            requirements=requirements,
            timestamp=datetime.now().isoformat()
        )
        
        # コード解析
        self.analysis_result = self.analyze_code(code, detected_language)
        
        return self.current_input, self.analysis_result

    def process_file_input(self, 
                          file_path: str,
                          project_root: str = None) -> Tuple[FileCodeInput, CodeAnalysisResult]:
        """
        単一ファイルを処理
        
        Args:
            file_path (str): ファイルパス
            project_root (str): プロジェクトルートディレクトリ
            
        Returns:
            Tuple[FileCodeInput, CodeAnalysisResult]: ファイル入力データと解析結果
        """
        try:
            # ファイル読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # ファイル情報取得
            file_stat = os.stat(file_path)
            file_path_obj = Path(file_path)
            
            # 相対パス計算
            relative_path = None
            if project_root:
                try:
                    relative_path = str(file_path_obj.relative_to(project_root))
                except ValueError:
                    relative_path = str(file_path_obj)
            
            # 言語判定
            language = self.detect_language_from_file(file_path, code_content)
            
            # ファイル入力データ作成
            file_input = FileCodeInput(
                file_path=file_path,
                code=code_content,
                language=language,
                file_size=file_stat.st_size,
                modified_time=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                relative_path=relative_path
            )
            
            # コード解析
            analysis = self.analyze_code(code_content, language)
            
            return file_input, analysis
            
        except Exception as e:
            # エラー時は空の結果を返す
            error_input = FileCodeInput(
                file_path=file_path,
                code=f"# エラー: ファイルを読み込めませんでした\n# {str(e)}",
                language='unknown'
            )
            
            error_analysis = CodeAnalysisResult(
                language='unknown',
                lines_of_code=0,
                functions=[],
                classes=[],
                imports=[],
                complexity_estimate='unknown',
                main_purpose=f"エラー: {str(e)}",
                suggested_improvements=[f"ファイル読み込みエラーを修正: {str(e)}"]
            )
            
            return error_input, error_analysis
    
    def process_multiple_files(self,
                              file_paths: List[str],
                              project_root: str = None,
                              description: str = None) -> Tuple[MultiFileInput, Dict[str, CodeAnalysisResult]]:
        """
        複数ファイルを処理
        
        Args:
            file_paths (List[str]): ファイルパスのリスト
            project_root (str): プロジェクトルートディレクトリ
            description (str): プロジェクトの説明
            
        Returns:
            Tuple[MultiFileInput, Dict[str, CodeAnalysisResult]]: 複数ファイル入力データと解析結果
        """
        files = []
        analyses = {}
        total_lines = 0
        
        for file_path in file_paths:
            file_input, analysis = self.process_file_input(file_path, project_root)
            files.append(file_input)
            analyses[file_path] = analysis
            total_lines += analysis.lines_of_code
        
        multi_input = MultiFileInput(
            files=files,
            total_files=len(files),
            total_lines=total_lines,
            project_root=project_root,
            description=description
        )
        
        return multi_input, analyses
    
    def detect_language_from_file(self, file_path: str, code_content: str = None) -> str:
        """
        ファイルパスと内容から言語を判定
        
        Args:
            file_path (str): ファイルパス
            code_content (str): ファイルの内容（オプション）
            
        Returns:
            str: 判定された言語
        """
        # 拡張子による判定
        extension = Path(file_path).suffix.lower()
        
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp'
        }
        
        if extension in extension_map:
            return extension_map[extension]
        
        # 内容による判定（拡張子で判定できない場合）
        if code_content:
            return self.detect_language(code_content)
        
        return 'unknown'
    
    def generate_multi_file_context(self, 
                                   multi_input: MultiFileInput,
                                   analyses: Dict[str, CodeAnalysisResult]) -> Dict[str, Any]:
        """
        複数ファイルのプロンプト生成用コンテキストを作成
        
        Args:
            multi_input (MultiFileInput): 複数ファイル入力データ
            analyses (Dict[str, CodeAnalysisResult]): 各ファイルの解析結果
            
        Returns:
            Dict[str, Any]: プロンプト生成に必要なコンテキスト
        """
        # 言語別統計
        language_stats = {}
        all_functions = []
        all_classes = []
        all_imports = []
        complexity_levels = []
        
        for file_input in multi_input.files:
            analysis = analyses[file_input.file_path]
            
            # 言語別統計
            lang = analysis.language
            if lang not in language_stats:
                language_stats[lang] = {'files': 0, 'lines': 0}
            language_stats[lang]['files'] += 1
            language_stats[lang]['lines'] += analysis.lines_of_code
            
            # 全体の要素を収集
            all_functions.extend(analysis.functions)
            all_classes.extend(analysis.classes)
            all_imports.extend(analysis.imports)
            complexity_levels.append(analysis.complexity_estimate)
        
        # メイン言語を特定
        main_language = max(language_stats.keys(), 
                          key=lambda x: language_stats[x]['lines'])
        
        # プロジェクト構造の概要
        file_structure = []
        for file_input in multi_input.files:
            rel_path = file_input.relative_path or os.path.basename(file_input.file_path)
            analysis = analyses[file_input.file_path]
            file_structure.append({
                'path': rel_path,
                'language': analysis.language,
                'lines': analysis.lines_of_code,
                'functions': len(analysis.functions),
                'classes': len(analysis.classes)
            })
        
        context = {
            "project_type": "multi_file_project",
            "main_language": main_language,
            "language_stats": language_stats,
            "total_files": multi_input.total_files,
            "total_lines": multi_input.total_lines,
            "file_structure": file_structure,
            "all_functions": list(set(all_functions))[:20],  # 最大20個
            "all_classes": list(set(all_classes))[:10],      # 最大10個
            "unique_imports": list(set(all_imports))[:15],   # 最大15個
            "complexity_distribution": dict(Counter(complexity_levels)),
            "project_root": multi_input.project_root,
            "description": multi_input.description,
            "suggested_focus": self._determine_project_focus(multi_input, analyses)
        }
        
        return context
    
    def _determine_project_focus(self, 
                               multi_input: MultiFileInput, 
                               analyses: Dict[str, CodeAnalysisResult]) -> List[str]:
        """プロジェクトの焦点を特定"""
        focus_areas = []
        
        # ファイル数による判定
        if multi_input.total_files > 10:
            focus_areas.append("大規模プロジェクトの構造最適化")
        elif multi_input.total_files > 5:
            focus_areas.append("モジュール間の依存関係整理")
        
        # 言語による判定
        purposes = [analysis.main_purpose for analysis in analyses.values()]
        if "Web API/アプリケーション開発" in purposes:
            focus_areas.append("API設計とパフォーマンス")
        if "データ処理・分析" in purposes:
            focus_areas.append("データパイプラインの最適化")
        if "機械学習モデル" in purposes:
            focus_areas.append("MLモデルのデプロイメント")
        
        # 複雑度による判定
        complex_files = [
            analysis for analysis in analyses.values()
            if analysis.complexity_estimate == 'complex'
        ]
        if len(complex_files) > 2:
            focus_areas.append("コード複雑度の削減")
        
        return focus_areas or ["コード品質の向上"]
    
    def export_multi_file_analysis(self, 
                                  multi_input: MultiFileInput,
                                  analyses: Dict[str, CodeAnalysisResult],
                                  output_path: str = "multi_file_analysis.json") -> str:
        """
        複数ファイル解析結果をエクスポート
        
        Args:
            multi_input (MultiFileInput): 複数ファイル入力データ
            analyses (Dict[str, CodeAnalysisResult]): 解析結果
            output_path (str): 出力ファイルパス
            
        Returns:
            str: エクスポートファイルパス
        """
        from collections import Counter
        
        export_data = {
            "project_info": {
                "total_files": multi_input.total_files,
                "total_lines": multi_input.total_lines,
                "project_root": multi_input.project_root,
                "description": multi_input.description,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "files": []
        }
        
        for file_input in multi_input.files:
            analysis = analyses[file_input.file_path]
            file_data = {
                "path": file_input.relative_path or file_input.file_path,
                "language": file_input.language,
                "size": file_input.file_size,
                "modified_time": file_input.modified_time,
                "analysis": {
                    "lines_of_code": analysis.lines_of_code,
                    "functions": analysis.functions,
                    "classes": analysis.classes,
                    "imports": analysis.imports[:10],  # 最大10個
                    "complexity": analysis.complexity_estimate,
                    "main_purpose": analysis.main_purpose,
                    "suggestions": analysis.suggested_improvements
                }
            }
            export_data["files"].append(file_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def generate_prompt_context(self) -> Dict[str, Any]:
        """
        プロンプト生成用のコンテキストを作成
        
        Returns:
            Dict[str, Any]: プロンプト生成に必要なコンテキスト
        """
        if not self.current_input or not self.analysis_result:
            raise ValueError("コード入力が処理されていません")
        
        context = {
            "code_snippet": self.current_input.code[:1000],  # 最初の1000文字
            "language": self.analysis_result.language,
            "code_structure": {
                "functions": self.analysis_result.functions,
                "classes": self.analysis_result.classes,
                "imports": self.analysis_result.imports
            },
            "complexity": self.analysis_result.complexity_estimate,
            "main_purpose": self.analysis_result.main_purpose,
            "lines_of_code": self.analysis_result.lines_of_code,
            "title": self.current_input.title,
            "description": self.current_input.description,
            "requirements": self.current_input.requirements,
            "suggestions": self.analysis_result.suggested_improvements
        }
        
        return context
    
    def format_code_with_syntax_highlight(self, code: str, language: str) -> str:
        """
        シンタックスハイライト付きHTMLを生成
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            
        Returns:
            str: HTML形式のハイライト済みコード
        """
        try:
            lexer = get_lexer_by_name(language, stripall=True)
            formatter = HtmlFormatter(style='monokai', linenos=True)
            return highlight(code, lexer, formatter)
        except:
            # フォールバック: プレーンテキスト
            return f"<pre><code>{code}</code></pre>"
    
    def export_code_analysis(self, output_path: str = "code_analysis.json") -> str:
        """
        コード解析結果をエクスポート
        
        Args:
            output_path (str): 出力ファイルパス
            
        Returns:
            str: エクスポートファイルパス
        """
        if not self.current_input or not self.analysis_result:
            raise ValueError("エクスポートするデータがありません")
        
        export_data = {
            "input": {
                "code": self.current_input.code,
                "language": self.current_input.language,
                "title": self.current_input.title,
                "description": self.current_input.description,
                "requirements": self.current_input.requirements,
                "timestamp": self.current_input.timestamp
            },
            "analysis": {
                "language": self.analysis_result.language,
                "lines_of_code": self.analysis_result.lines_of_code,
                "functions": self.analysis_result.functions,
                "classes": self.analysis_result.classes,
                "imports": self.analysis_result.imports,
                "complexity": self.analysis_result.complexity_estimate,
                "main_purpose": self.analysis_result.main_purpose,
                "suggestions": self.analysis_result.suggested_improvements
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return output_path