"""
コード入力処理モジュール
PoCデモプログラムのソースコードを受け取り、プロンプト生成に活用
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import ast
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter


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