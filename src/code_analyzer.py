"""
高度なコード解析モジュール
コードの構造、パターン、品質を詳細に解析
"""

import re
import ast
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class CodeMetrics:
    """コードメトリクスデータクラス"""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    maintainability_index: float = 0.0
    code_coverage_estimate: float = 0.0
    test_ratio: float = 0.0
    documentation_ratio: float = 0.0


@dataclass
class CodePattern:
    """コードパターンデータクラス"""
    pattern_type: str
    pattern_name: str
    occurrences: int
    locations: List[int] = field(default_factory=list)
    description: str = ""


@dataclass
class DependencyInfo:
    """依存関係情報データクラス"""
    internal_dependencies: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    circular_dependencies: List[str] = field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)


class CodeAnalyzer:
    """高度なコード解析クラス"""
    
    # デザインパターンの定義
    DESIGN_PATTERNS = {
        'singleton': {
            'keywords': ['_instance', 'getInstance', '__new__'],
            'description': 'シングルトンパターン'
        },
        'factory': {
            'keywords': ['Factory', 'create', 'build'],
            'description': 'ファクトリーパターン'
        },
        'observer': {
            'keywords': ['Observer', 'subscribe', 'notify', 'addEventListener'],
            'description': 'オブザーバーパターン'
        },
        'strategy': {
            'keywords': ['Strategy', 'algorithm', 'execute'],
            'description': 'ストラテジーパターン'
        },
        'decorator': {
            'keywords': ['@', 'Decorator', 'wrap'],
            'description': 'デコレーターパターン'
        }
    }
    
    # コードスメルの定義
    CODE_SMELLS = {
        'long_method': {
            'threshold': 30,
            'description': '長すぎるメソッド'
        },
        'large_class': {
            'threshold': 500,
            'description': '大きすぎるクラス'
        },
        'too_many_parameters': {
            'threshold': 5,
            'description': 'パラメータが多すぎる'
        },
        'duplicate_code': {
            'threshold': 3,
            'description': '重複コード'
        },
        'dead_code': {
            'keywords': ['unused', 'deprecated', 'FIXME'],
            'description': 'デッドコード'
        }
    }
    
    def __init__(self):
        """初期化"""
        self.code = None
        self.language = None
        self.ast_tree = None
        
    def analyze_python_ast(self, code: str) -> Dict[str, Any]:
        """
        Python ASTを詳細解析
        
        Args:
            code (str): Pythonソースコード
            
        Returns:
            Dict[str, Any]: AST解析結果
        """
        try:
            self.ast_tree = ast.parse(code)
            
            # 各種ノードをカウント
            node_counts = defaultdict(int)
            function_info = []
            class_info = []
            
            for node in ast.walk(self.ast_tree):
                node_type = type(node).__name__
                node_counts[node_type] += 1
                
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'returns': self._get_annotation(node.returns),
                        'docstring': ast.get_docstring(node),
                        'line_start': node.lineno,
                        'complexity': self._calculate_function_complexity(node)
                    }
                    function_info.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    cls_info = {
                        'name': node.name,
                        'bases': [self._get_base_name(b) for b in node.bases],
                        'methods': methods,
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'docstring': ast.get_docstring(node),
                        'line_start': node.lineno
                    }
                    class_info.append(cls_info)
            
            return {
                'node_statistics': dict(node_counts),
                'functions': function_info,
                'classes': class_info,
                'imports': self._extract_imports(),
                'global_variables': self._extract_global_variables(),
                'constants': self._extract_constants()
            }
            
        except SyntaxError as e:
            return {'error': f'構文エラー: {str(e)}'}
        except Exception as e:
            return {'error': f'解析エラー: {str(e)}'}
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """関数の循環的複雑度を計算"""
        complexity = 1  # 基本複雑度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _get_decorator_name(self, decorator_node) -> str:
        """デコレーター名を取得"""
        if isinstance(decorator_node, ast.Name):
            return decorator_node.id
        elif isinstance(decorator_node, ast.Call):
            if isinstance(decorator_node.func, ast.Name):
                return decorator_node.func.id
        return 'unknown'
    
    def _get_base_name(self, base_node) -> str:
        """基底クラス名を取得"""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{self._get_base_name(base_node.value)}.{base_node.attr}"
        return 'unknown'
    
    def _get_annotation(self, annotation_node) -> Optional[str]:
        """型アノテーションを取得"""
        if annotation_node is None:
            return None
        if isinstance(annotation_node, ast.Name):
            return annotation_node.id
        elif isinstance(annotation_node, ast.Constant):
            return str(annotation_node.value)
        return 'complex_type'
    
    def _extract_imports(self) -> List[Dict[str, Any]]:
        """インポート文を抽出"""
        imports = []
        if not self.ast_tree:
            return imports
            
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'type': 'import'
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'type': 'from_import'
                    })
        return imports
    
    def _extract_global_variables(self) -> List[str]:
        """グローバル変数を抽出"""
        globals_vars = []
        if not self.ast_tree:
            return globals_vars
            
        for node in self.ast_tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals_vars.append(target.id)
        return globals_vars
    
    def _extract_constants(self) -> List[Dict[str, Any]]:
        """定数を抽出（大文字の変数）"""
        constants = []
        if not self.ast_tree:
            return constants
            
        for node in self.ast_tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        value = None
                        if isinstance(node.value, ast.Constant):
                            value = node.value.value
                        constants.append({
                            'name': target.id,
                            'value': value
                        })
        return constants
    
    def detect_patterns(self, code: str, language: str) -> List[CodePattern]:
        """
        デザインパターンを検出
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            
        Returns:
            List[CodePattern]: 検出されたパターン
        """
        patterns = []
        
        for pattern_name, pattern_def in self.DESIGN_PATTERNS.items():
            occurrences = 0
            locations = []
            
            for keyword in pattern_def['keywords']:
                for i, line in enumerate(code.split('\n'), 1):
                    if keyword in line:
                        occurrences += 1
                        locations.append(i)
            
            if occurrences > 0:
                patterns.append(CodePattern(
                    pattern_type='design_pattern',
                    pattern_name=pattern_name,
                    occurrences=occurrences,
                    locations=locations[:5],  # 最初の5箇所のみ
                    description=pattern_def['description']
                ))
        
        return patterns
    
    def detect_code_smells(self, code: str, language: str) -> List[Dict[str, Any]]:
        """
        コードスメルを検出
        
        Args:
            code (str): ソースコード  
            language (str): プログラミング言語
            
        Returns:
            List[Dict[str, Any]]: 検出されたコードスメル
        """
        smells = []
        lines = code.split('\n')
        
        # 長すぎるメソッドの検出
        if language == 'python':
            current_function = None
            function_lines = 0
            
            for i, line in enumerate(lines):
                if re.match(r'^\s*def\s+\w+\s*\(', line):
                    if current_function and function_lines > self.CODE_SMELLS['long_method']['threshold']:
                        smells.append({
                            'type': 'long_method',
                            'location': current_function,
                            'severity': 'medium',
                            'message': f'{current_function}は{function_lines}行で長すぎます'
                        })
                    current_function = re.search(r'def\s+(\w+)', line).group(1)
                    function_lines = 0
                elif current_function:
                    function_lines += 1
        
        # 重複コードの簡易検出
        code_blocks = {}
        for i in range(len(lines) - 3):
            block = '\n'.join(lines[i:i+3])
            if len(block.strip()) > 50:  # 意味のあるブロックのみ
                if block in code_blocks:
                    code_blocks[block].append(i)
                else:
                    code_blocks[block] = [i]
        
        for block, locations in code_blocks.items():
            if len(locations) >= self.CODE_SMELLS['duplicate_code']['threshold']:
                smells.append({
                    'type': 'duplicate_code',
                    'locations': locations,
                    'severity': 'high',
                    'message': f'重複コードが{len(locations)}箇所で検出されました'
                })
        
        return smells
    
    def calculate_metrics(self, code: str, language: str) -> CodeMetrics:
        """
        コードメトリクスを計算
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            
        Returns:
            CodeMetrics: 計算されたメトリクス
        """
        metrics = CodeMetrics()
        lines = code.split('\n')
        
        # 基本メトリクス
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        
        # ドキュメント率
        metrics.documentation_ratio = comment_lines / total_lines if total_lines > 0 else 0
        
        # テストコードの割合
        test_lines = len([l for l in lines if 'test' in l.lower() or 'assert' in l])
        metrics.test_ratio = test_lines / code_lines if code_lines > 0 else 0
        
        # 保守性インデックス（簡易版）
        # MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
        # ここではシンプルな推定値を使用
        if code_lines > 0:
            import math
            volume_estimate = code_lines * 10  # 簡易推定
            complexity_estimate = code_lines / 10  # 簡易推定
            metrics.maintainability_index = max(0, min(100,
                171 - 5.2 * math.log(volume_estimate + 1) 
                - 0.23 * complexity_estimate 
                - 16.2 * math.log(code_lines + 1)
            ))
        
        # Pythonの場合、ASTから詳細な複雑度を計算
        if language == 'python':
            try:
                tree = ast.parse(code)
                total_complexity = 0
                function_count = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_count += 1
                        total_complexity += self._calculate_function_complexity(node)
                
                metrics.cyclomatic_complexity = total_complexity
                metrics.cognitive_complexity = total_complexity * 1.2  # 簡易推定
                
            except:
                pass
        
        return metrics
    
    def analyze_dependencies(self, code: str, language: str) -> DependencyInfo:
        """
        依存関係を解析
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            
        Returns:
            DependencyInfo: 依存関係情報
        """
        deps = DependencyInfo()
        
        if language == 'python':
            # Pythonの依存関係解析
            import_pattern = r'(?:from\s+([\w\.]+)\s+)?import\s+([\w\s,]+)'
            for match in re.finditer(import_pattern, code):
                module = match.group(1) or match.group(2).split(',')[0].strip()
                
                # 標準ライブラリかどうかを判定（簡易版）
                stdlib = ['os', 'sys', 're', 'json', 'datetime', 'math', 'random',
                         'collections', 'itertools', 'functools', 'typing']
                
                if module.startswith('.'):
                    deps.internal_dependencies.append(module)
                elif module in stdlib:
                    pass  # 標準ライブラリは除外
                else:
                    deps.external_dependencies.append(module)
        
        elif language in ['javascript', 'typescript']:
            # JavaScript/TypeScriptの依存関係解析
            import_pattern = r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'
            require_pattern = r'require\s*\(["\']([^"\']+)["\']\)'
            
            for match in re.finditer(import_pattern, code):
                module = match.group(1)
                if module.startswith('.'):
                    deps.internal_dependencies.append(module)
                else:
                    deps.external_dependencies.append(module)
            
            for match in re.finditer(require_pattern, code):
                module = match.group(1)
                if module.startswith('.'):
                    deps.internal_dependencies.append(module)
                else:
                    deps.external_dependencies.append(module)
        
        # 依存関係グラフの構築（簡易版）
        for dep in deps.internal_dependencies:
            deps.dependency_graph[dep] = []
        
        return deps
    
    def generate_improvement_suggestions(self, 
                                        code: str, 
                                        language: str,
                                        patterns: List[CodePattern],
                                        smells: List[Dict[str, Any]],
                                        metrics: CodeMetrics) -> List[Dict[str, Any]]:
        """
        改善提案を生成
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            patterns (List[CodePattern]): 検出されたパターン
            smells (List[Dict[str, Any]]): 検出されたコードスメル
            metrics (CodeMetrics): コードメトリクス
            
        Returns:
            List[Dict[str, Any]]: 改善提案リスト
        """
        suggestions = []
        
        # メトリクスベースの提案
        if metrics.maintainability_index < 50:
            suggestions.append({
                'priority': 'high',
                'category': 'maintainability',
                'suggestion': 'コードの保守性が低いです。関数の分割やリファクタリングを検討してください',
                'impact': '保守コストの削減'
            })
        
        if metrics.documentation_ratio < 0.1:
            suggestions.append({
                'priority': 'medium',
                'category': 'documentation',
                'suggestion': 'ドキュメントが不足しています。コメントやdocstringを追加してください',
                'impact': '可読性の向上'
            })
        
        if metrics.test_ratio < 0.1:
            suggestions.append({
                'priority': 'high',
                'category': 'testing',
                'suggestion': 'テストコードが不足しています。単体テストを追加してください',
                'impact': '品質保証の向上'
            })
        
        # コードスメルベースの提案
        for smell in smells:
            if smell['type'] == 'long_method':
                suggestions.append({
                    'priority': 'medium',
                    'category': 'refactoring',
                    'suggestion': f"{smell['location']}を小さな関数に分割してください",
                    'impact': '可読性と再利用性の向上'
                })
            elif smell['type'] == 'duplicate_code':
                suggestions.append({
                    'priority': 'high',
                    'category': 'refactoring',
                    'suggestion': '重複コードを共通関数として抽出してください',
                    'impact': 'DRY原則の遵守'
                })
        
        # パターンベースの提案
        pattern_names = [p.pattern_name for p in patterns]
        if 'singleton' in pattern_names and 'factory' not in pattern_names:
            suggestions.append({
                'priority': 'low',
                'category': 'design',
                'suggestion': 'ファクトリーパターンの使用を検討してください',
                'impact': 'オブジェクト生成の柔軟性向上'
            })
        
        return suggestions
    
    def export_analysis_report(self, 
                              code: str,
                              language: str,
                              output_path: str = "code_analysis_report.json") -> str:
        """
        詳細な解析レポートをエクスポート
        
        Args:
            code (str): ソースコード
            language (str): プログラミング言語
            output_path (str): 出力ファイルパス
            
        Returns:
            str: エクスポートファイルパス
        """
        # 各種解析を実行
        patterns = self.detect_patterns(code, language)
        smells = self.detect_code_smells(code, language)
        metrics = self.calculate_metrics(code, language)
        dependencies = self.analyze_dependencies(code, language)
        suggestions = self.generate_improvement_suggestions(
            code, language, patterns, smells, metrics
        )
        
        # Python ASTの解析
        ast_analysis = {}
        if language == 'python':
            ast_analysis = self.analyze_python_ast(code)
        
        # レポート作成
        report = {
            'language': language,
            'metrics': {
                'cyclomatic_complexity': metrics.cyclomatic_complexity,
                'cognitive_complexity': metrics.cognitive_complexity,
                'maintainability_index': metrics.maintainability_index,
                'documentation_ratio': metrics.documentation_ratio,
                'test_ratio': metrics.test_ratio
            },
            'patterns': [
                {
                    'type': p.pattern_type,
                    'name': p.pattern_name,
                    'occurrences': p.occurrences,
                    'description': p.description
                } for p in patterns
            ],
            'code_smells': smells,
            'dependencies': {
                'internal': dependencies.internal_dependencies,
                'external': dependencies.external_dependencies
            },
            'ast_analysis': ast_analysis,
            'improvement_suggestions': suggestions
        }
        
        # ファイルに保存
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return output_path