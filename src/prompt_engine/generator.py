"""
プロンプト生成エンジンのメインモジュール
AIエンジニア向けのプロンプト生成システム
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic
import logging

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """プロンプトタイプ列挙"""
    DATA_ANALYSIS = "data_analysis"
    IMAGE_RECOGNITION = "image_recognition"
    TEXT_PROCESSING = "text_processing"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    API_TESTING = "api_testing"
    GENERAL_POC = "general_poc"


@dataclass
class PromptRequest:
    """プロンプト生成リクエスト"""
    prompt_type: PromptType
    user_requirements: str
    context: str = ""
    domain: str = ""
    output_format: str = "structured"
    constraints: List[str] = None
    examples: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.examples is None:
            self.examples = []


@dataclass
class GeneratedPrompt:
    """生成されたプロンプト"""
    content: str
    metadata: Dict[str, Any]
    quality_score: float = 0.0
    suggestions: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class PromptGenerator:
    """メインプロンプト生成クラス"""
    
    def __init__(self, anthropic_client: anthropic.AsyncAnthropic, 
                 model_name: str = "claude-3-sonnet-20240229",
                 temperature: float = 0.7):
        self.client = anthropic_client
        self.model_name = model_name
        self.temperature = temperature
        self.generation_history: List[GeneratedPrompt] = []
        
    async def generate_prompt(self, request: PromptRequest) -> GeneratedPrompt:
        """プロンプトを生成"""
        try:
            logger.info(f"プロンプト生成開始: タイプ={request.prompt_type.value}")
            
            # プロンプトタイプに応じた生成ロジック選択
            generation_prompt = self._build_generation_prompt(request)
            
            # Claude APIでプロンプト生成
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=self.temperature,
                messages=[{"role": "user", "content": generation_prompt}]
            )
            
            generated_content = response.content[0].text.strip()
            
            # メタデータ構築
            metadata = {
                "prompt_type": request.prompt_type.value,
                "domain": request.domain,
                "output_format": request.output_format,
                "constraints_count": len(request.constraints),
                "examples_count": len(request.examples),
                "generation_model": self.model_name,
                "generation_temperature": self.temperature
            }
            
            # 生成されたプロンプトオブジェクト作成
            generated_prompt = GeneratedPrompt(
                content=generated_content,
                metadata=metadata
            )
            
            # 履歴に追加
            self.generation_history.append(generated_prompt)
            
            logger.info(f"プロンプト生成完了: 長さ={len(generated_content)}文字")
            return generated_prompt
            
        except Exception as e:
            logger.error(f"プロンプト生成エラー: {str(e)}")
            raise
    
    def _build_generation_prompt(self, request: PromptRequest) -> str:
        """プロンプトタイプ別の生成プロンプトを構築"""
        
        base_instruction = f"""
あなたは優秀なプロンプトエンジニアです。
AIエンジニア向けのPoC開発支援用プロンプトを生成してください。

【要求内容】
{request.user_requirements}

【文脈・背景】
{request.context}

【対象分野】
{request.domain if request.domain else request.prompt_type.value}

【出力形式要件】
{request.output_format}
"""
        
        if request.constraints:
            base_instruction += f"""
【制約条件】
{chr(10).join(f'- {constraint}' for constraint in request.constraints)}
"""
        
        if request.examples:
            base_instruction += f"""
【参考例】
{chr(10).join(f'{i+1}. {example}' for i, example in enumerate(request.examples))}
"""
        
        # プロンプトタイプ別の専門指示
        type_specific_instruction = self._get_type_specific_instruction(request.prompt_type)
        
        return base_instruction + type_specific_instruction
    
    def _get_type_specific_instruction(self, prompt_type: PromptType) -> str:
        """プロンプトタイプ別の専門指示を取得"""
        
        instructions = {
            PromptType.DATA_ANALYSIS: """

【データ分析プロンプト作成指針】
- データの種類と形式を明確に指定
- 分析手法と統計的要件を含める
- ビジネス価値につながる洞察を促す
- 可視化要件を具体的に記述
- 解釈と推奨アクションを求める

生成するプロンプトは実務的で、統計的根拠を重視し、
ビジネス担当者にも理解できる説明を含むものにしてください。
""",
            
            PromptType.IMAGE_RECOGNITION: """

【画像認識プロンプト作成指針】
- 対象画像の種類と特徴を明確に定義
- 認識精度の要件を数値で指定
- エラーハンドリングと例外ケースを考慮
- 実行環境の制約を反映
- 結果のフォーマットをJSON等で具体化

生成するプロンプトは技術的精度と実用性を両立し、
デプロイメント要件も考慮したものにしてください。
""",
            
            PromptType.TEXT_PROCESSING: """

【テキスト処理プロンプト作成指針】
- 処理対象テキストの特性を明確化
- NLP技術の選定理由を含める
- 品質評価指標を具体的に設定
- 多言語・文体への対応を考慮
- コンテキスト理解の重要性を強調

生成するプロンプトは言語学的正確性と
実用的効率性のバランスを取ったものにしてください。
""",
            
            PromptType.REQUIREMENTS_ANALYSIS: """

【要件分析プロンプト作成指針】
- ステークホルダー視点の網羅性
- 機能/非機能要件の体系的整理
- 優先度とリスクの定量的評価
- 実現可能性の技術的検証
- 将来拡張性の考慮

生成するプロンプトは実践的で、
プロジェクト成功に直結する要件抽出を促すものにしてください。
""",
            
            PromptType.API_TESTING: """

【APIテストプロンプト作成指針】
- テスト観点の網羅性（正常系・異常系・境界値）
- セキュリティテストの考慮
- パフォーマンステストの要件
- 自動化可能なテスト設計
- 継続的インテグレーション対応

生成するプロンプトは実践的で、
実際のAPI品質保証に役立つものにしてください。
""",
            
            PromptType.GENERAL_POC: """

【汎用PoC用プロンプト作成指針】
- PoC特有の制約（時間・リソース）を考慮
- 迅速な結果出力と検証可能性
- ステークホルダーへの説明容易性
- 本格開発への発展性
- リスク要因の早期発見

生成するプロンプトは実用的で、
PoC成功に必要な要素を効率的に満たすものにしてください。
"""
        }
        
        return instructions.get(prompt_type, instructions[PromptType.GENERAL_POC])
    
    async def improve_prompt(self, original_prompt: GeneratedPrompt, 
                           feedback: str, suggestions: List[str] = None) -> GeneratedPrompt:
        """既存プロンプトを改善"""
        if suggestions is None:
            suggestions = []
            
        try:
            logger.info("プロンプト改善開始")
            
            improvement_prompt = f"""
あなたはプロンプト改善の専門家です。

【改善対象プロンプト】
{original_prompt.content}

【フィードバック】
{feedback}

【具体的改善提案】
{chr(10).join(f'- {suggestion}' for suggestion in suggestions)}

【改善要求】
上記のフィードバックと提案に基づいて、プロンプトを改善してください。

【改善観点】
1. より明確で具体的な指示
2. 必要な文脈情報の追加
3. 出力形式のより詳細な指定
4. 制約条件の明確化
5. 品質向上のための例示追加

改善されたプロンプトのみを出力してください。説明は不要です。
"""
            
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=self.temperature,
                messages=[{"role": "user", "content": improvement_prompt}]
            )
            
            improved_content = response.content[0].text.strip()
            
            # 改善されたプロンプトオブジェクト作成
            improved_metadata = original_prompt.metadata.copy()
            improved_metadata.update({
                "improved_from": original_prompt.created_at,
                "improvement_feedback": feedback,
                "improvement_count": improved_metadata.get("improvement_count", 0) + 1
            })
            
            improved_prompt = GeneratedPrompt(
                content=improved_content,
                metadata=improved_metadata,
                suggestions=suggestions
            )
            
            # 履歴に追加
            self.generation_history.append(improved_prompt)
            
            logger.info("プロンプト改善完了")
            return improved_prompt
            
        except Exception as e:
            logger.error(f"プロンプト改善エラー: {str(e)}")
            raise
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """生成統計を取得"""
        if not self.generation_history:
            return {"total_generations": 0}
        
        stats = {
            "total_generations": len(self.generation_history),
            "by_type": {},
            "average_length": 0,
            "recent_generations": []
        }
        
        # タイプ別集計
        type_counts = {}
        total_length = 0
        
        for prompt in self.generation_history:
            prompt_type = prompt.metadata.get("prompt_type", "unknown")
            type_counts[prompt_type] = type_counts.get(prompt_type, 0) + 1
            total_length += len(prompt.content)
        
        stats["by_type"] = type_counts
        stats["average_length"] = total_length / len(self.generation_history)
        
        # 最近の生成履歴（最新5件）
        stats["recent_generations"] = [
            {
                "created_at": prompt.created_at,
                "prompt_type": prompt.metadata.get("prompt_type"),
                "length": len(prompt.content),
                "quality_score": prompt.quality_score
            }
            for prompt in self.generation_history[-5:]
        ]
        
        return stats
    
    def export_prompts(self, filepath: str, format: str = "json"):
        """生成したプロンプトをエクスポート"""
        try:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_prompts": len(self.generation_history),
                "prompts": [
                    {
                        "content": prompt.content,
                        "metadata": prompt.metadata,
                        "quality_score": prompt.quality_score,
                        "suggestions": prompt.suggestions,
                        "created_at": prompt.created_at
                    }
                    for prompt in self.generation_history
                ]
            }
            
            if format.lower() == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"サポートされていないフォーマット: {format}")
            
            logger.info(f"プロンプトをエクスポートしました: {filepath}")
            
        except Exception as e:
            logger.error(f"エクスポートエラー: {str(e)}")
            raise