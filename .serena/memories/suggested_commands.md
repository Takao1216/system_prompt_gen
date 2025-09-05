# Suggested Commands for System Prompt Gen Project

## Development Commands

### Environment Setup
```bash
# 仮想環境作成と有効化
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集してANTHROPIC_API_KEYを設定
```

### Running the Application
```bash
# FastAPI サーバー起動
python run.py
# または
uvicorn src.api.main:app --reload --host localhost --port 8000

# Jupyter Notebook起動
jupyter notebook notebook_v1.0.0.ipynb  # 安定版
jupyter notebook notebook_v1.1.0-dev.ipynb  # 開発版

# JupyterLab起動（日本語対応）
jupyter lab
```

### Testing & Validation
```bash
# システム検証スクリプト実行
python validate.py

# テスト実行
pytest tests/
pytest tests/ -v  # 詳細表示
pytest tests/ --cov=src --cov-report=html  # カバレッジレポート付き

# 特定のテストファイル実行
pytest tests/test_generator.py
pytest tests/test_evaluator.py
```

### Code Quality
```bash
# コードフォーマット（Black）
black src/ tests/
black --check src/ tests/  # チェックのみ

# Linting（Flake8）
flake8 src/ tests/

# 型チェック（MyPy）
mypy src/
```

### Git Commands
```bash
# ステータス確認
git status
git branch

# 新機能開発
git checkout -b feature/new-feature
git add .
git commit -m "Add: 新機能の説明"
git push origin feature/new-feature

# 開発ブランチ
git checkout develop
git pull origin develop
```

### Notebook Version Management
```bash
# 新バージョン開発開始
cp notebook_v1.0.0.ipynb notebook_v1.1.0-dev.ipynb

# ステージ移行
cp notebook_v1.1.0-dev.ipynb notebook_v1.1.0-alpha.ipynb
cp notebook_v1.1.0-alpha.ipynb notebook_v1.1.0-beta.ipynb
cp notebook_v1.1.0-beta.ipynb notebook_v1.1.0-rc.ipynb
cp notebook_v1.1.0-rc.ipynb notebook_v1.1.0.ipynb

# リリースパッケージ作成
cp notebook_v1.1.0.ipynb release/v1.1.0/notebook.ipynb
```

### API Testing
```bash
# API Documentation
# Browser: http://localhost:8000/docs (Swagger UI)
# Browser: http://localhost:8000/redoc (ReDoc)

# cURL Examples
# プロンプト生成
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt_type":"data_analysis","user_requirements":"売上分析"}'

# プロンプト評価
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"prompt_content":"プロンプト内容"}'
```

### Cleanup & Maintenance
```bash
# Notebook出力クリア
jupyter nbconvert --clear-output --inplace notebook_v*.ipynb

# キャッシュクリア
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 仮想環境再作成
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Darwin (macOS) Specific Commands
```bash
# ファイル検索
find . -name "*.py" -type f
grep -r "PromptGenerator" src/

# プロセス確認
lsof -i :8000  # ポート8000使用プロセス
ps aux | grep python

# 権限設定
chmod +x setup.py
chmod +x run.py
```

## Quick Debug Commands
```bash
# Python対話モード
python
>>> from src.generator import PromptGenerator
>>> gen = PromptGenerator()
>>> exit()

# 環境変数確認
echo $ANTHROPIC_API_KEY
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY', 'Not set'))"
```