#!/usr/bin/env python
"""
Validation script to test all components of the system_prompt_gen project.
実行方法: python validate.py
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数をロード
load_dotenv()

def check_environment():
    """環境変数とAPIキーのチェック"""
    print("=" * 60)
    print("1. 環境設定チェック")
    print("=" * 60)
    
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key and api_key != "your_anthropic_api_key_here":
        print("✅ ANTHROPIC_API_KEY: 設定済み")
        return True
    else:
        print("❌ ANTHROPIC_API_KEY: 未設定 (.envファイルを確認してください)")
        return False

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("\n" + "=" * 60)
    print("2. モジュールインポートチェック")
    print("=" * 60)
    
    modules_status = {}
    
    # Core modules
    try:
        from src.generator import PromptGenerator
        modules_status["PromptGenerator"] = "✅"
    except Exception as e:
        modules_status["PromptGenerator"] = f"❌ {e}"
    
    try:
        from src.evaluator import PromptEvaluator
        modules_status["PromptEvaluator"] = "✅"
    except Exception as e:
        modules_status["PromptEvaluator"] = f"❌ {e}"
    
    try:
        from src.templates.template_manager import TemplateManager
        modules_status["TemplateManager"] = "✅"
    except Exception as e:
        modules_status["TemplateManager"] = f"❌ {e}"
    
    # Optional modules
    try:
        import anthropic
        modules_status["anthropic"] = "✅"
    except ImportError:
        modules_status["anthropic"] = "⚠️ 未インストール (pip install anthropic)"
    
    try:
        import langchain
        modules_status["langchain"] = "✅ (オプション)"
    except ImportError:
        modules_status["langchain"] = "⚠️ 未インストール (オプション)"
    
    try:
        import fastapi
        modules_status["fastapi"] = "✅"
    except ImportError:
        modules_status["fastapi"] = "⚠️ 未インストール (pip install fastapi)"
    
    for module, status in modules_status.items():
        print(f"{module}: {status}")
    
    return all("❌" not in status for status in modules_status.values() if "オプション" not in status)

async def test_api_connection():
    """Claude API接続テスト"""
    print("\n" + "=" * 60)
    print("3. Claude API接続テスト")
    print("=" * 60)
    
    if not os.getenv("ANTHROPIC_API_KEY", "").startswith("sk-"):
        print("⚠️ 有効なAPIキーが設定されていません")
        return False
    
    try:
        import anthropic
        from src.generator import PromptGenerator
        
        # Updated model name
        generator = PromptGenerator(model="claude-3-5-sonnet-20241022")
        
        # シンプルなテストプロンプト
        test_prompt = await generator.generate_prompt(
            task_type="general_poc",
            requirements="API接続テスト"
        )
        
        if test_prompt:
            print("✅ API接続成功!")
            print(f"生成されたプロンプト (最初の100文字): {test_prompt[:100]}...")
            return True
        else:
            print("❌ プロンプト生成失敗")
            return False
            
    except anthropic.NotFoundError as e:
        print(f"❌ モデルが見つかりません: {e}")
        print("💡 ヒント: claude-3-5-sonnet-20241022 を使用してください")
        return False
    except Exception as e:
        print(f"❌ API接続エラー: {e}")
        return False

def test_template_manager():
    """テンプレートマネージャーのテスト"""
    print("\n" + "=" * 60)
    print("4. テンプレートマネージャーテスト")
    print("=" * 60)
    
    try:
        from src.templates.template_manager import TemplateManager
        
        manager = TemplateManager()
        
        # デフォルトテンプレートの確認
        templates = manager.list_templates()
        print(f"利用可能なテンプレート数: {len(templates)}")
        for template_name in templates[:3]:  # 最初の3つを表示
            print(f"  - {template_name}")
        
        # テンプレート取得テスト
        template = manager.get_template("data_analysis")
        if template:
            print("✅ テンプレート取得成功")
            return True
        else:
            print("❌ テンプレート取得失敗")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_evaluator():
    """プロンプト評価器のテスト"""
    print("\n" + "=" * 60)
    print("5. プロンプト評価器テスト")
    print("=" * 60)
    
    try:
        from src.evaluator import PromptEvaluator
        
        evaluator = PromptEvaluator()
        
        test_prompt = "CSVファイルを読み込んで、データの統計情報を表示してください。"
        
        scores = evaluator.evaluate(test_prompt)
        
        print("評価結果:")
        for metric, score in scores.items():
            status = "✅" if score >= 0.6 else "⚠️"
            print(f"  {status} {metric}: {score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def check_fastapi():
    """FastAPI設定のチェック"""
    print("\n" + "=" * 60)
    print("6. FastAPI設定チェック")
    print("=" * 60)
    
    try:
        from src.api.main import app
        import uvicorn
        
        print("✅ FastAPIアプリケーション: ロード成功")
        print("\n起動コマンド例:")
        print("  python run.py")
        print("  または")
        print("  uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def main():
    """メイン検証関数"""
    print("\n" + "🔍 System Prompt Generator 検証スクリプト " + "🔍")
    print("=" * 60)
    
    results = []
    
    # 1. 環境チェック
    results.append(("環境設定", check_environment()))
    
    # 2. インポートチェック
    results.append(("モジュール", test_imports()))
    
    # 3. テンプレートマネージャー
    results.append(("テンプレート", test_template_manager()))
    
    # 4. 評価器
    results.append(("評価器", test_evaluator()))
    
    # 5. API接続（APIキーがある場合のみ）
    if os.getenv("ANTHROPIC_API_KEY", "").startswith("sk-"):
        results.append(("API接続", await test_api_connection()))
    
    # 6. FastAPI
    results.append(("FastAPI", check_fastapi()))
    
    # サマリー
    print("\n" + "=" * 60)
    print("検証結果サマリー")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 成功" if passed else "❌ 失敗"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 全てのチェックが成功しました！")
        print("\n次のステップ:")
        print("1. Jupyter Notebookを起動: jupyter notebook")
        print("2. FastAPIサーバーを起動: python run.py")
        print("3. ブラウザでアクセス: http://localhost:8000")
    else:
        print("\n⚠️ いくつかのチェックが失敗しました。")
        print("上記のエラーメッセージを確認して修正してください。")
        print("\n💡 ヒント:")
        print("1. .envファイルにANTHROPIC_API_KEYを設定")
        print("2. 依存関係をインストール: pip install -r requirements.txt")
        print("3. モデル名を claude-3-5-sonnet-20241022 に更新")

if __name__ == "__main__":
    # nest_asyncioを使用してJupyter環境でも動作するように
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    
    asyncio.run(main())