# Task Completion Checklist

## When a Task is Completed

### 1. Code Quality Checks
```bash
# フォーマット
black src/ tests/

# Linting
flake8 src/ tests/

# 型チェック（可能な場合）
mypy src/
```

### 2. Testing
```bash
# 関連テストの実行
pytest tests/ -v

# 新機能の場合はテスト追加
# tests/test_[feature].py を作成
```

### 3. Validation
```bash
# システム全体の検証
python validate.py

# Notebook動作確認（変更した場合）
# 各セルを順番に実行して確認
```

### 4. Documentation Update
- 新機能の場合はREADME.md更新
- APIエンドポイント追加時はAPI仕様記載
- Notebook変更時はNOTEBOOK_GUIDE.md確認

### 5. Environment Check
```bash
# 新しい依存関係を追加した場合
# requirements.txtを更新
pip freeze > requirements_temp.txt
# 必要なパッケージのみrequirements.txtに反映
```

### 6. Git Operations
```bash
# 変更内容確認
git status
git diff

# ステージング
git add [files]

# コミット（意味のあるメッセージで）
git commit -m "Add/Fix/Update: 具体的な変更内容"
```

### 7. Notebook Specific
- 出力セルのクリア（リリース前）
- メタデータ更新（バージョン、更新日）
- 個人情報・APIキーが含まれていないか確認

### 8. Final Checks
- [ ] コードが動作する
- [ ] テストが通る
- [ ] ドキュメントが最新
- [ ] 不要なデバッグコード削除
- [ ] コメントが適切
- [ ] エラーハンドリング実装

## Common Issues to Check

1. **Import Error対策**
   - 相対インポートと絶対インポートの整合性
   - オプショナルな依存関係のtry-except処理

2. **API Key管理**
   - ハードコードされていないか
   - .envファイルから読み込んでいるか

3. **非同期処理**
   - Jupyter環境でnest_asyncio使用
   - await/asyncの適切な使用

4. **メモリリーク**
   - 大きなデータの適切な削除
   - ファイルハンドルのclose

## Release Preparation
```bash
# リリース準備の場合
1. notebook出力クリア
2. .env → .env.sample変換
3. release/vX.X.X/へコピー
4. CHANGELOG.md更新
5. バージョンタグ付け
```