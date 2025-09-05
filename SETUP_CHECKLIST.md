# ✅ セットアップチェックリスト

このチェックリストを使用して、Jupyter Notebookを実行する前の準備状況を確認してください。

## 📝 事前準備チェックリスト

### 🔐 APIキー取得
- [ ] Anthropic社のアカウントを作成済み
- [ ] Claude APIキーを取得済み（[console.anthropic.com](https://console.anthropic.com)）
- [ ] APIキーが `sk-ant-api03-` で始まることを確認

### 💻 Python環境
- [ ] Python 3.8以上がインストール済み
- [ ] pipが最新版（`pip install --upgrade pip`）
- [ ] 仮想環境を作成済み（推奨）

```bash
# 仮想環境の作成例
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

## 🚀 インストール手順

### Step 1: リポジトリのクローン/ダウンロード
```bash
git clone <repository-url>
cd system_prompt_gen
```
✅ チェック: `ls`コマンドで`notebook.ipynb`が見えること

### Step 2: 依存関係のインストール
```bash
pip install -r requirements.txt
```
✅ チェック: エラーなく完了すること

### Step 3: 環境変数の設定
```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集
# ANTHROPIC_API_KEY="あなたのAPIキー"を設定
```
✅ チェック: `.env`ファイルにAPIキーが設定されていること

### Step 4: ファイル構造の確認
```bash
# 必須ファイルの存在確認
ls src/generator.py
ls src/evaluator.py
ls src/templates/template_manager.py
```
✅ チェック: 全てのファイルが存在すること

### Step 5: 動作検証
```bash
python validate.py
```
✅ チェック: 以下の項目が全て✅になること:
- 環境設定
- モジュール
- テンプレート
- API接続

## 📊 検証結果の見方

### ✅ 成功例
```
============================================================
検証結果サマリー
============================================================
環境設定: ✅ 成功
モジュール: ✅ 成功
テンプレート: ✅ 成功
評価器: ✅ 成功
API接続: ✅ 成功
FastAPI: ✅ 成功

🎉 全てのチェックが成功しました！
```

### ❌ 失敗例と対処法

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `環境設定: ❌` | APIキー未設定 | `.env`ファイルにAPIキーを設定 |
| `モジュール: ❌` | ファイル不足 | 必要なPythonファイルを確認 |
| `API接続: ❌` | 無効なAPIキー | APIキーが正しいか確認 |
| `Model not found` | 古いモデル名 | `claude-3-5-sonnet-20241022`を使用 |

## 🎯 Notebook実行チェックリスト

### 実行前の最終確認
- [ ] `validate.py`が全て成功
- [ ] Jupyter Notebookがインストール済み
- [ ] ブラウザが利用可能

### Notebook起動
```bash
jupyter notebook notebook.ipynb
```

### 実行順序
1. [ ] **セクション1（環境設定）を最初に実行**
   - 依存ライブラリ確認
   - 環境変数読み込み
   - API接続テスト

2. [ ] **セクション2-4を順番に実行**（オプション）
   - 理論説明
   - テンプレート
   - ワークフロー

3. [ ] **セクション5（プロンプト生成）を実行**
   - 実際の生成テスト
   - 品質評価
   - 改善プロセス

## 🆘 よくある質問

### Q: APIキーはどこで取得？
A: [console.anthropic.com](https://console.anthropic.com)でアカウント作成後、APIキーを生成

### Q: 必要最小限の設定は？
A: `.env`ファイルのAPIキー設定のみ必須。他はオプション。

### Q: LangChainエラーが出る
A: LangChainはオプションなので、エラーは無視して続行可能

### Q: どのセルから実行すべき？
A: 必ずセクション1の環境設定から実行。その後は任意。

### Q: 料金はかかる？
A: Claude APIの使用量に応じて課金されます（Anthropicの料金体系を確認）

## 📈 実行成功の確認

以下が表示されれば成功:

```python
✅ プロンプト生成エンジン初期化完了
  - Generator: claude-3-5-sonnet-20241022
  - Evaluator: claude-3-5-sonnet-20241022
```

## 🎉 準備完了！

全てのチェックが完了したら、Notebookを使用してプロンプト生成を開始できます。

---

**トラブル時**: `python validate.py`で診断 → エラーメッセージを確認 → 上記の対処法を試す