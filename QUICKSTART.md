# 🚀 クイックスタートガイド

## システムプロンプト生成器 for AI Engineer PoC

このガイドでは、システムプロンプト生成器を最短でセットアップして使用開始する方法を説明します。

## 📋 前提条件

- Python 3.8以上
- Claude API キー（Anthropic社から取得）

## ⚡ 5分でセットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境設定

`.env`ファイルを編集してAPIキーを設定：

```bash
# .envファイルを開く
ANTHROPIC_API_KEY="sk-ant-api03-xxxxx"  # あなたのAPIキーに置き換え
```

### 3. 動作確認

```bash
# 全コンポーネントの検証
python validate.py
```

全てのチェックが✅になることを確認してください。

## 🎯 使い方（3つの方法）

### 方法1: Jupyter Notebook（推奨）

最も簡単で視覚的な方法：

```bash
jupyter notebook notebook.ipynb
```

Notebookを開いて、セル を順番に実行してください。

### 方法2: Web API

RESTful APIとして使用：

```bash
# サーバー起動
python run.py

# 別のターミナルでAPIをテスト
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "data_analysis",
    "requirements": "売上データを分析して傾向を見つける"
  }'
```

APIドキュメント: http://localhost:8000/docs

### 方法3: Pythonスクリプト

```python
import asyncio
from src.generator import PromptGenerator

async def main():
    generator = PromptGenerator(model="claude-3-5-sonnet-20241022")
    
    prompt = await generator.generate_prompt(
        task_type="data_analysis",
        requirements="売上データの分析",
        constraints="実行時間は5分以内"
    )
    
    print(prompt)

asyncio.run(main())
```

## 📦 利用可能なタスクタイプ

1. **data_analysis** - データ分析PoC
2. **image_recognition** - 画像認識PoC  
3. **text_processing** - テキスト処理PoC
4. **requirements_analysis** - 要件定義支援
5. **api_testing** - APIテスト
6. **general_poc** - 汎用PoC

## 💡 よくあるユースケース

### データ分析プロンプト生成

```python
prompt = await generator.generate_prompt(
    task_type="data_analysis",
    requirements="月次売上データから季節性トレンドを抽出",
    context={
        "data_format": "CSV",
        "period": "2年間",
        "columns": "date, product_id, sales, quantity"
    }
)
```

### API テストケース生成

```python
prompt = await generator.generate_prompt(
    task_type="api_testing",
    requirements="ユーザー認証APIの包括的テスト",
    context={
        "endpoint": "/api/auth/login",
        "method": "POST",
        "auth_type": "JWT"
    }
)
```

## 🔧 トラブルシューティング

### API キーエラー

```
❌ ANTHROPIC_API_KEY: 未設定
```

→ `.env`ファイルにAPIキーを設定してください

### モデルエラー

```
404 Error: Model not found
```

→ モデル名を`claude-3-5-sonnet-20241022`に設定してください

### インポートエラー

```
No module named 'anthropic'
```

→ `pip install -r requirements.txt`を実行してください

## 📚 詳細ドキュメント

- [README.md](README.md) - プロジェクト概要
- [notebook.ipynb](notebook.ipynb) - インタラクティブなチュートリアル
- API Docs: http://localhost:8000/docs (サーバー起動後)

## 🆘 サポート

問題が発生した場合：

1. `python validate.py`で診断を実行
2. エラーメッセージを確認
3. このガイドのトラブルシューティングセクションを参照

---

**Happy Prompting! 🎉**