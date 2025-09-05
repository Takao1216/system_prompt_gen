# System Prompt Gen Project Overview

## Purpose
AI Engineers向けのPoC開発支援用プロンプト生成システム。システム開発経験の少ないAIエンジニアが、効果的なプロンプトを生成・改善するためのツールセット。

## Tech Stack
- **Language**: Python 3.8+
- **LLM Framework**: LangChain, LangGraph
- **AI API**: Anthropic Claude API (claude-3-5-sonnet-20241022)
- **Web Framework**: FastAPI with Uvicorn
- **Data Processing**: Pandas, NumPy
- **Frontend**: Jupyter Notebook/Lab (日本語対応)
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Development Tools**: black, flake8, mypy

## Main Features
1. **自動プロンプト生成**: 6種類のプロンプトタイプ対応
2. **品質評価システム**: 5つの評価軸での自動評価
3. **LangGraphワークフロー**: プロンプトの自動改善サイクル
4. **FastAPI Web API**: RESTful API提供
5. **テンプレート管理**: 再利用可能なプロンプトテンプレート
6. **Jupyterノートブック**: インタラクティブな実験環境

## Project Structure
```
system_prompt_gen/
├── src/
│   ├── api/                 # FastAPI実装
│   ├── prompt_engine/       # コアエンジン
│   ├── langgraph_workflows/ # ワークフロー
│   └── templates/           # テンプレート管理
├── tests/                   # テストスイート
├── notebooks/              # Notebook管理
├── release/                # リリースパッケージ
└── notebook_v*.ipynb       # バージョン管理されたNotebook
```

## Version Management
- **Notebook Versioning**: semantic versioning (v{MAJOR}.{MINOR}.{PATCH}[-{STAGE}])
- **Current Stable**: v1.0.0
- **Current Development**: v1.1.0-dev
- **Release Directory**: release/v1.0.0/ (sanitized for distribution)