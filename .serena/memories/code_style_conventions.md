# Code Style and Conventions

## Python Code Style

### Naming Conventions
- **Classes**: PascalCase (e.g., `PromptGenerator`, `PromptEvaluator`)
- **Functions/Methods**: snake_case (e.g., `generate_prompt()`, `evaluate_quality()`)
- **Variables**: snake_case (e.g., `prompt_content`, `quality_scores`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `ANTHROPIC_AVAILABLE`, `DEFAULT_MODEL`)
- **Private methods**: Leading underscore (e.g., `_evaluate_clarity()`)

### Type Hints
```python
# 使用例
from typing import Dict, List, Optional, Any

def generate_prompt(
    prompt_type: str,
    user_requirements: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    pass
```

### Docstrings
```python
def evaluate(self, prompt: str) -> Dict[str, float]:
    """
    プロンプトの品質を評価
    
    Args:
        prompt (str): 評価対象のプロンプト
        
    Returns:
        Dict[str, float]: 各評価軸のスコア（0.0-10.0）
    """
```

### Import Organization
```python
# 標準ライブラリ
import os
import sys
from typing import Dict, List, Optional

# サードパーティライブラリ
import anthropic
from langchain.schema import BaseMessage

# ローカルモジュール
from src.generator import PromptGenerator
from src.evaluator import PromptEvaluator
```

## File Structure Conventions

### Module Organization
- One class per file for main components
- Related utilities in same module
- `__init__.py` for package exports

### Test Files
- Mirror source structure in `tests/`
- Prefix with `test_` (e.g., `test_generator.py`)
- Test class names: `TestClassName`
- Test methods: `test_method_name()`

## Error Handling
```python
try:
    # Anthropic APIのインポート試行
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    
# 利用可能性チェック
if not ANTHROPIC_AVAILABLE:
    return {"error": "Anthropic library not available"}
```

## Japanese Comments
- 日本語コメントOK（プロジェクトの性質上）
- 重要な処理には日本語説明を追加
- APIドキュメントは日本語/英語併記

## Async/Await Pattern
```python
import nest_asyncio
nest_asyncio.apply()  # Jupyter環境でのasync対応

async def async_generate():
    # 非同期処理
    pass
```

## Configuration Management
- 環境変数は`.env`ファイルで管理
- `python-dotenv`で読み込み
- デフォルト値を必ず設定
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY", "")
```

## Notebook Conventions
- セクション番号とタイトル明記
- 各セクションに説明マークダウン
- 出力はリリース時にクリア
- メタデータセルを最初に配置

## Git Commit Messages
```
Add: 新機能追加
Fix: バグ修正
Update: 既存機能の更新
Refactor: リファクタリング
Docs: ドキュメント更新
Test: テスト追加・修正
```

## Quality Standards
- テストカバレッジ目標: 80%以上
- Flake8準拠（E501は除外可）
- Black自動フォーマット適用
- MyPy型チェック通過