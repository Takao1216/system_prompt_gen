"""
プロンプト生成器モジュール
"""

import os
from typing import Dict, Optional, Any
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class PromptGenerator:
    """プロンプト生成器クラス"""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        初期化
        
        Args:
            model: 使用するClaude モデル名
        """
        self.model = model
        self.client = None
        
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key and api_key != "your_anthropic_api_key_here":
                self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_prompt(
        self, 
        task_type: str,
        requirements: str,
        context: Optional[Dict] = None,
        constraints: Optional[str] = None,
        examples: Optional[str] = None
    ) -> str:
        """
        タスクタイプと要件に基づいてプロンプトを生成
        
        Args:
            task_type: タスクの種類
            requirements: 要件の説明
            context: 追加のコンテキスト情報
            constraints: 制約条件
            examples: 例示
            
        Returns:
            生成されたプロンプト
        """
        if not self.client:
            # Claudeが利用できない場合はテンプレートベースの生成
            return self._generate_template_based(
                task_type, requirements, context, constraints, examples
            )
        
        # Claudeを使用したプロンプト生成
        system_prompt = """
        あなたはAIエンジニア向けのプロンプトを生成する専門家です。
        以下の要素を含む明確で効果的なプロンプトを生成してください：
        1. 明確な役割定義
        2. 具体的なタスクの説明
        3. 期待する出力形式
        4. 制約条件
        5. 必要に応じて例示
        """
        
        user_message = f"""
        以下の要件に基づいてプロンプトを生成してください：
        
        タスクタイプ: {task_type}
        要件: {requirements}
        """
        
        if context:
            user_message += f"\nコンテキスト: {json.dumps(context, ensure_ascii=False)}"
        if constraints:
            user_message += f"\n制約条件: {constraints}"
        if examples:
            user_message += f"\n例: {examples}"
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text if message.content else ""
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._generate_template_based(
                task_type, requirements, context, constraints, examples
            )
    
    def _generate_template_based(
        self,
        task_type: str,
        requirements: str,
        context: Optional[Dict] = None,
        constraints: Optional[str] = None,
        examples: Optional[str] = None
    ) -> str:
        """
        テンプレートベースのプロンプト生成（フォールバック）
        """
        prompt_parts = []
        
        # 役割定義
        role_mapping = {
            "data_analysis": "あなたは経験豊富なデータサイエンティストです。",
            "image_recognition": "あなたはコンピュータビジョンの専門家です。",
            "text_processing": "あなたは自然言語処理の専門家です。",
            "requirements_analysis": "あなたは要求分析の専門家です。",
            "api_testing": "あなたはAPI開発とテストの専門家です。",
            "general_poc": "あなたはPoCプロジェクトの技術コンサルタントです。"
        }
        
        role = role_mapping.get(task_type, "あなたはAIアシスタントです。")
        prompt_parts.append(role)
        
        # タスク説明
        prompt_parts.append(f"\n【タスク】\n{requirements}")
        
        # コンテキスト
        if context:
            prompt_parts.append(f"\n【コンテキスト】")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
        
        # 制約条件
        if constraints:
            prompt_parts.append(f"\n【制約条件】\n{constraints}")
        
        # 例示
        if examples:
            prompt_parts.append(f"\n【例】\n{examples}")
        
        # 出力要件
        prompt_parts.append("\n【出力要件】")
        prompt_parts.append("1. 明確で構造化された回答を提供してください")
        prompt_parts.append("2. 技術的な詳細と実装の具体例を含めてください")
        prompt_parts.append("3. 潜在的な課題とその解決策を示してください")
        
        return "\n".join(prompt_parts)
    
    def improve_prompt(self, original_prompt: str, feedback: str) -> str:
        """
        フィードバックに基づいてプロンプトを改善
        
        Args:
            original_prompt: 元のプロンプト
            feedback: 改善のためのフィードバック
            
        Returns:
            改善されたプロンプト
        """
        if not self.client:
            # シンプルな改善
            return f"{original_prompt}\n\n【改善点】\n{feedback}"
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system="あなたはプロンプトエンジニアリングの専門家です。",
                messages=[
                    {
                        "role": "user", 
                        "content": f"""
                        以下のプロンプトをフィードバックに基づいて改善してください：
                        
                        元のプロンプト:
                        {original_prompt}
                        
                        フィードバック:
                        {feedback}
                        
                        改善されたプロンプトを生成してください。
                        """
                    }
                ]
            )
            return message.content[0].text if message.content else original_prompt
        except Exception as e:
            print(f"改善エラー: {e}")
            return f"{original_prompt}\n\n【改善点】\n{feedback}"