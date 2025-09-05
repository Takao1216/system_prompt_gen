#!/usr/bin/env python3
"""
プロンプト生成システム セットアップスクリプト
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Pythonバージョンチェック"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]}以上が必要です")
        print(f"   現在のバージョン: {sys.version}")
        return False
    
    print(f"✅ Python {current_version[0]}.{current_version[1]} を使用")
    return True


def create_virtual_environment():
    """仮想環境の作成"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ 仮想環境は既に存在します")
        return True
    
    print("📦 仮想環境を作成中...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ 仮想環境を作成しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 仮想環境の作成に失敗: {e}")
        return False


def get_pip_command():
    """適切なpipコマンドを取得"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "pip")
    else:  # Unix/Linux/Mac
        return os.path.join("venv", "bin", "pip")


def install_dependencies():
    """依存ライブラリのインストール"""
    pip_cmd = get_pip_command()
    
    if not os.path.exists(pip_cmd):
        print("⚠️  仮想環境のpipが見つかりません。システムのpipを使用します。")
        pip_cmd = "pip"
    
    print("📚 依存ライブラリをインストール中...")
    
    # pipをアップグレード
    try:
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        print("✅ pipをアップグレードしました")
    except subprocess.CalledProcessError:
        print("⚠️  pipのアップグレードをスキップ")
    
    # requirements.txtからインストール
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ 依存ライブラリをインストールしました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依存ライブラリのインストールに失敗: {e}")
        return False


def setup_environment_file():
    """環境設定ファイルのセットアップ"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .envファイルは既に存在します")
        
        # APIキーが設定されているかチェック
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_claude_api_key_here' in content:
                print("\n⚠️  重要: ANTHROPIC_API_KEYを実際のAPIキーに置き換えてください")
                print("   .envファイルを編集して、your_claude_api_key_here を置き換えてください")
    else:
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ .env.example から .env ファイルを作成しました")
            print("\n⚠️  重要: .envファイルを編集してANTHROPIC_API_KEYを設定してください")
        else:
            print("⚠️  .env.example ファイルが見つかりません")
    
    return True


def create_necessary_directories():
    """必要なディレクトリを作成"""
    directories = [
        "src/templates/data",
        "logs",
        "outputs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ 必要なディレクトリを作成しました")
    return True


def print_next_steps():
    """次のステップを表示"""
    print("\n" + "=" * 60)
    print("🎉 セットアップ完了！")
    print("=" * 60)
    print("\n📋 次のステップ:")
    print("\n1. 環境変数の設定:")
    print("   .envファイルを編集してANTHROPIC_API_KEYを設定してください")
    print("\n2. 仮想環境の有効化:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    
    print("\n3. システムの起動:")
    print("   python run.py")
    print("\n4. ブラウザでアクセス:")
    print("   http://localhost:8000")
    print("\n5. API文書を確認:")
    print("   http://localhost:8000/docs")
    print("\n6. Jupyterノートブックを使用:")
    print("   jupyter notebook notebook.ipynb")
    print("\n" + "=" * 60)


def main():
    """メインセットアップ処理"""
    print("=" * 60)
    print("🚀 プロンプト生成システム セットアップ")
    print("=" * 60)
    print()
    
    # Pythonバージョンチェック
    if not check_python_version():
        sys.exit(1)
    
    # 仮想環境作成
    if not create_virtual_environment():
        print("\n⚠️  仮想環境の作成をスキップして続行します")
    
    # 依存ライブラリインストール
    if not install_dependencies():
        print("\n❌ セットアップに失敗しました")
        sys.exit(1)
    
    # 環境設定ファイル
    setup_environment_file()
    
    # 必要なディレクトリ作成
    create_necessary_directories()
    
    # 次のステップ表示
    print_next_steps()


if __name__ == "__main__":
    main()