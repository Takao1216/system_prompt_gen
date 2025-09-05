# system_prompt_gen

## 📝 概要

AIエンジニア向けのPoC開発支援用プロンプト生成システムです。システム開発経験の少ないAIエンジニアが、効果的なプロンプトを生成・改善するためのツールを提供します。

### ✨ 主な機能

- 🤖 **自動プロンプト生成**: 6種類のプロンプトタイプに対応（データ分析、画像認識、テキスト処理など）
- 📊 **品質評価システム**: 5つの評価軸でプロンプトの品質を自動評価
- 🔄 **LangGraphワークフロー**: プロンプトの自動改善サイクル実装
- 🌐 **FastAPI Web API**: RESTful APIでの利用が可能
- 📚 **テンプレート管理**: 再利用可能なプロンプトテンプレート
- 📓 **Jupyterノートブック**: インタラクティブな実験環境

## 🚀 クイックスタート

### 1. セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/system_prompt_gen.git
cd system_prompt_gen

# セットアップスクリプトを実行
python setup.py
```

### 2. 環境設定

`.env` ファイルを編集してAPIキーを設定：

```bash
# .envファイルを編集
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. システム起動

```bash
# 仮想環境を有効化（セットアップ後）
source venv/bin/activate  # Mac/Linux
# または
venv\Scripts\activate  # Windows

# システムを起動
python run.py
```

### 4. アクセス

- 🌐 Webインターフェース: http://localhost:8000
- 📚 API文書（Swagger UI）: http://localhost:8000/docs
- 📖 API仕様書（ReDoc）: http://localhost:8000/redoc

## 📦 インストール（手動）

### 前提条件

- Python 3.8以上
- pip

### 手順

1. 依存ライブラリのインストール：
```bash
pip install -r requirements.txt
```

2. 環境変数の設定：
```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

3. 実行：
```bash
python run.py
```

## 🔧 API使用例

### プロンプト生成

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "prompt_type": "data_analysis",
        "user_requirements": "売上データを分析して季節性を特定したい",
        "context": "ECサイトの月次売上データ（過去2年分）",
        "domain": "eコマース"
    }
)

result = response.json()
print(result["prompt"])
```

### プロンプト評価

```python
response = requests.post(
    "http://localhost:8000/api/v1/evaluate",
    json={
        "prompt_content": "生成されたプロンプト内容",
        "original_request": "元の要求",
        "context": "背景情報"
    }
)

evaluation = response.json()
print(f"品質スコア: {evaluation['quality_scores']['overall']}/10")
```

### 自動改善ワークフロー

```python
response = requests.post(
    "http://localhost:8000/api/v1/workflow",
    json={
        "user_request": "画像分類モデルのテストケースを作成",
        "context": "製品画像の分類システム",
        "prompt_type": "image_recognition"
    }
)

workflow_result = response.json()
print(f"最終プロンプト: {workflow_result['final_prompt']}")
print(f"改善回数: {workflow_result['iteration_count']}")
```

## 📓 Jupyterノートブック

インタラクティブな実験環境を使用：

```bash
jupyter notebook notebook.ipynb
```

ノートブックには以下のセクションが含まれています：
1. 環境設定
2. プロンプト生成理論
3. テンプレート管理
4. LangGraphワークフロー
5. 実践的なデモ

## 🏗️ プロジェクト構成

```
system_prompt_gen/
├── src/
│   ├── api/                 # FastAPI実装
│   │   └── main.py         # APIエンドポイント
│   ├── prompt_engine/       # コアエンジン
│   │   ├── generator.py    # プロンプト生成
│   │   └── evaluator.py    # 品質評価
│   ├── langgraph_workflows/ # ワークフロー
│   │   └── prompt_workflow.py
│   └── templates/           # テンプレート管理
│       └── template_manager.py
├── tests/                   # テストスイート
├── notebook.ipynb          # Jupyterノートブック
├── requirements.txt        # 依存ライブラリ
├── .env.example           # 環境変数サンプル
├── setup.py               # セットアップスクリプト
└── run.py                 # 起動スクリプト
```

## 🧪 テスト実行

```bash
# 全テストを実行
pytest tests/

# カバレッジ付きでテスト
pytest tests/ --cov=src --cov-report=html
```

## 🤝 貢献方法

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを開く

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🔗 関連リンク

- [Anthropic Claude API](https://www.anthropic.com/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [FastAPI](https://fastapi.tiangolo.com/)

## 💬 サポート

問題が発生した場合は、[Issues](https://github.com/yourusername/system_prompt_gen/issues)で報告してください。