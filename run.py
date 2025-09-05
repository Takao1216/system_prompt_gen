#!/usr/bin/env python3
"""
プロンプト生成システム起動スクリプト
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """メインエントリーポイント"""
    # 環境変数読み込み
    load_dotenv()
    
    # 必須環境変数チェック
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your_claude_api_key_here':
        print("=" * 50)
        print("❌ エラー: ANTHROPIC_API_KEYが設定されていません")
        print("=" * 50)
        print("\n設定方法:")
        print("1. .envファイルを開く")
        print("2. ANTHROPIC_API_KEY=your_claude_api_key_here を実際のAPIキーに置き換える")
        print("3. 保存して再度実行する")
        print("\nAPIキーの取得方法:")
        print("https://console.anthropic.com/ でアカウントを作成してAPIキーを取得してください")
        print("=" * 50)
        sys.exit(1)
    
    # 設定値取得
    host = os.getenv('APP_HOST', 'localhost')
    port = int(os.getenv('APP_PORT', '8000'))
    debug = os.getenv('DEBUG_MODE', 'true').lower() == 'true'
    
    print("=" * 50)
    print("🚀 プロンプト生成システムを起動しています...")
    print("=" * 50)
    print(f"📍 URL: http://{host}:{port}")
    print(f"📚 API文書: http://{host}:{port}/docs")
    print(f"🔧 デバッグモード: {debug}")
    print(f"🤖 モデル: {os.getenv('DEFAULT_MODEL', 'claude-3-sonnet-20240229')}")
    print("=" * 50)
    print("\n終了するには Ctrl+C を押してください\n")
    
    try:
        # FastAPIアプリケーションを起動
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "error"
        )
    except KeyboardInterrupt:
        print("\n\n👋 システムを終了しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()