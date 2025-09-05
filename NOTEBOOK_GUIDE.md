# 📓 Jupyter Notebook 利用ガイド

## 概要
このガイドでは、`notebook.ipynb`を正常に実行するために必要なファイル、設定、手順を説明します。

---

## 🔧 必要なファイル一覧

### 1. 環境設定ファイル

#### **.env** (必須)
APIキーと環境変数を設定するファイルです。

```env
# Claude API設定（必須）
ANTHROPIC_API_KEY="あなたのAPIキーをここに設定"

# LangSmith設定（オプション）
LANGSMITH_API_KEY="your_langsmith_api_key_here"
LANGSMITH_PROJECT="prompt-generation-poc"
LANGSMITH_TRACING="true"

# アプリケーション設定
APP_HOST="localhost"
APP_PORT="8000"
DEFAULT_MODEL="claude-3-5-sonnet-20241022"
```

⚠️ **重要**: `ANTHROPIC_API_KEY`は必ず有効なAPIキーを設定してください

### 2. Pythonモジュール

#### **src/generator.py** (必須)
プロンプト生成器の実装

主な機能:
- `PromptGenerator`クラス
- `generate_prompt()`メソッド: プロンプト生成
- `improve_prompt()`メソッド: プロンプト改善

#### **src/evaluator.py** (必須)
プロンプト品質評価器の実装

主な機能:
- `PromptEvaluator`クラス
- `evaluate()`メソッド: 品質評価
- `get_improvement_suggestions()`メソッド: 改善提案

#### **src/templates/template_manager.py** (必須)
テンプレート管理システム

主な機能:
- `TemplateManager`クラス
- 5つのデフォルトテンプレート
- カスタムテンプレート作成機能

#### **src/api/main.py** (オプション)
FastAPI実装（Web API利用時のみ必要）

### 3. 依存関係ファイル

#### **requirements.txt** (必須)
必要なPythonパッケージのリスト

主要パッケージ:
```
anthropic>=0.18.0        # Claude API (必須)
langchain>=0.1.0         # LangChain (オプション)
langgraph>=0.0.40        # LangGraph (オプション)
fastapi>=0.104.0         # FastAPI (オプション)
pandas>=2.1.0            # データ処理
numpy>=1.24.0            # 数値計算
jupyter>=1.0.0           # Jupyter Notebook
nest-asyncio>=1.5.0      # 非同期処理サポート
```

---

## 📋 セットアップ手順

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. APIキーの設定
`.env`ファイルを作成し、APIキーを設定:
```bash
# .env.exampleをコピー
cp .env.example .env

# .envファイルを編集してAPIキーを設定
# ANTHROPIC_API_KEY="sk-ant-api03-xxxxx"
```

### 3. ディレクトリ構造の確認
```
system_prompt_gen/
├── .env                              # 環境変数（要作成）
├── notebook.ipynb                    # Jupyterノートブック
├── requirements.txt                  # 依存関係
├── src/
│   ├── __init__.py
│   ├── generator.py                  # プロンプト生成器
│   ├── evaluator.py                  # 品質評価器
│   ├── templates/
│   │   ├── __init__.py
│   │   └── template_manager.py       # テンプレート管理
│   └── api/
│       └── main.py                   # FastAPI（オプション）
└── validate.py                       # 検証スクリプト
```

### 4. 動作確認
```bash
# 検証スクリプトを実行
python validate.py

# 全てのチェックが✅になることを確認
```

---

## 🚀 Notebook の起動

### 方法1: コマンドラインから
```bash
jupyter notebook notebook.ipynb
```

### 方法2: JupyterLabを使用
```bash
jupyter lab
# notebook.ipynbを開く
```

### 方法3: VS Codeを使用
1. VS Codeで`notebook.ipynb`を開く
2. Jupyter拡張機能がインストールされていることを確認
3. カーネルを選択して実行

---

## 📖 Notebook の構成

### セクション1: 環境設定
- 依存ライブラリのインストール確認
- 環境変数の読み込み
- API接続テスト

### セクション2: プロンプト生成理論
- 品質評価指標の定義
- プロンプトパターン分析
- 構成要素の説明

### セクション3: テンプレート管理
- デフォルトテンプレート（5種類）
- カスタムテンプレート作成
- テンプレート統計

### セクション4: LangGraphワークフロー
- ワークフロー状態定義
- プロンプト改善サイクル
- 品質評価と改善

### セクション5: プロンプト生成エンジン
- 実際のプロンプト生成
- 品質評価の実行
- 改善プロセスのデモ

---

## ⚠️ トラブルシューティング

### エラー1: ModuleNotFoundError
```
解決方法: pip install -r requirements.txt
```

### エラー2: APIキーエラー
```
解決方法: .envファイルにANTHROPIC_API_KEYを設定
```

### エラー3: モデルが見つからない
```
解決方法: モデル名を claude-3-5-sonnet-20241022 に更新
```

### エラー4: ImportError (LangGraph関連)
```
解決方法: LangGraphはオプションなので、エラーは無視可能
```

### エラー5: asyncio関連エラー
```
解決方法: nest_asyncio がインストールされていることを確認
```

---

## 🔍 動作確認チェックリスト

- [ ] `.env`ファイルが存在する
- [ ] `ANTHROPIC_API_KEY`が設定されている
- [ ] `requirements.txt`の全パッケージがインストール済み
- [ ] `src/generator.py`が存在する
- [ ] `src/evaluator.py`が存在する  
- [ ] `src/templates/template_manager.py`が存在する
- [ ] `python validate.py`が成功する
- [ ] Jupyter Notebookが起動できる

---

## 💡 使用のヒント

### 最小構成での実行
必須ファイルのみで実行可能:
- `.env` (APIキー設定)
- `src/generator.py`
- `src/evaluator.py`
- `src/templates/template_manager.py`

### オプション機能
以下は必須ではありません:
- LangChain/LangGraph
- FastAPI
- LangSmith

### セル実行順序
1. **必ず最初にセクション1を実行**（環境設定）
2. その後は任意の順序で実行可能
3. セクション5は他のセクションの内容を使用

---

## 📞 サポート

問題が発生した場合:

1. `python validate.py`で診断
2. このガイドのトラブルシューティングを確認
3. エラーメッセージを確認して対処

---

**最終更新**: 2025年1月
**対応モデル**: claude-3-5-sonnet-20241022