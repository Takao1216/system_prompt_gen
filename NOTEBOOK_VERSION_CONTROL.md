# 📓 Notebook バージョン管理ガイド

## 概要

このプロジェクトでは、Jupyter Notebookのバージョン管理を以下の規則で行います。

## 📁 ファイル命名規則

### 形式
```
notebook_v{MAJOR}.{MINOR}.{PATCH}[-{STAGE}].ipynb
```

### ステージ識別子
- **-dev**: 開発中（Development）
- **-alpha**: アルファ版（内部テスト）
- **-beta**: ベータ版（限定公開テスト）
- **-rc**: リリース候補（Release Candidate）
- *(なし)*: 正式リリース版

### 例
- `notebook_v1.0.0.ipynb` - 正式リリース版
- `notebook_v1.1.0-dev.ipynb` - 開発中バージョン
- `notebook_v1.1.0-beta.ipynb` - ベータテスト版
- `notebook_v1.1.0-rc.ipynb` - リリース候補版
- `notebook_v1.1.0.ipynb` - 正式リリース版

## 🔄 開発フロー

```
v1.0.0 (リリース済み)
    ↓
v1.1.0-dev (開発中) ← 現在ここ
    ↓
v1.1.0-alpha (内部テスト)
    ↓
v1.1.0-beta (限定公開)
    ↓
v1.1.0-rc (最終確認)
    ↓
v1.1.0 (正式リリース)
```

## 📊 現在のバージョン状態

| ファイル名 | バージョン | ステータス | 説明 |
|-----------|------------|-----------|------|
| `notebook_v1.0.0.ipynb` | v1.0.0 | ✅ リリース済み | 初期リリース版（安定版） |
| `notebook_v1.1.0-dev.ipynb` | v1.1.0-dev | 🔧 開発中 | 履歴管理・バッチ処理・コード入力機能追加 |

## 🏷️ バージョン番号の増加規則

### PATCH (v1.0.X)
- バグ修正
- タイポ修正
- 軽微な説明文の改善
- 依存パッケージのバージョン更新

### MINOR (v1.X.0)
- 新しいセルやセクションの追加
- 新しい機能やテンプレートの追加
- UIの改善
- パフォーマンスの改善

### MAJOR (vX.0.0)
- 大規模な構造変更
- 後方互換性のない変更
- 根本的な設計思想の変更
- APIの大幅な変更

## 📝 開発ルール

### 1. 開発開始時
```bash
# 現在の安定版から開発版を作成
cp notebook_v1.0.0.ipynb notebook_v1.1.0-dev.ipynb
```

### 2. 開発中
- 常に`-dev`サフィックス付きで作業
- 頻繁にバックアップを作成
- 大きな変更前にコミット

### 3. テスト段階
```bash
# アルファ版として保存
cp notebook_v1.1.0-dev.ipynb notebook_v1.1.0-alpha.ipynb

# ベータ版として保存
cp notebook_v1.1.0-alpha.ipynb notebook_v1.1.0-beta.ipynb
```

### 4. リリース準備
```bash
# リリース候補版
cp notebook_v1.1.0-beta.ipynb notebook_v1.1.0-rc.ipynb

# 最終リリース
cp notebook_v1.1.0-rc.ipynb notebook_v1.1.0.ipynb
```

### 5. リリースパッケージ更新
```bash
# リリースディレクトリにコピー
cp notebook_v1.1.0.ipynb release/v1.1.0/notebook.ipynb
```

## 🔖 メタデータ管理

各Notebookの最初のセルに以下のメタデータを含める：

```markdown
# System Prompt Generator for AI Engineers
## Version: 1.1.0-dev
## Last Modified: 2025-01-05
## Author: AI Engineer Team
## Stage: Development
```

## 📋 チェックリスト

### 新バージョン開発開始時
- [ ] 現在の安定版からコピー
- [ ] `-dev`サフィックスを追加
- [ ] メタデータセルを更新
- [ ] NOTEBOOK_VERSION_CONTROL.mdを更新

### リリース前
- [ ] 全セルの動作確認
- [ ] APIキーなど個人情報の除去
- [ ] 出力セルのクリア（必要に応じて）
- [ ] ドキュメントの更新
- [ ] メタデータの最終確認

## 🗂️ バックアップ戦略

```
notebooks/
├── current/              # 現在作業中
│   └── notebook_v1.1.0-dev.ipynb
├── stable/               # 安定版
│   └── notebook_v1.0.0.ipynb
└── archive/              # 過去のバージョン
    ├── notebook_v0.9.0.ipynb
    └── ...
```

## 💡 ベストプラクティス

1. **頻繁なバックアップ**: 大きな変更前に必ずバックアップ
2. **明確なコミットメッセージ**: 変更内容を詳細に記録
3. **段階的リリース**: dev → alpha → beta → rc → release
4. **後方互換性の維持**: 可能な限り既存機能を保持
5. **ドキュメント同期**: Notebookとドキュメントのバージョンを同期

## 📈 バージョン履歴

| バージョン | リリース日 | 主な変更点 |
|-----------|-----------|-----------|
| v1.0.0 | 2025-01-05 | 初期リリース |
| v1.1.0-dev | 開発中 | 新機能追加予定 |

---

最終更新: 2025-01-05
現在の開発バージョン: v1.1.0-dev