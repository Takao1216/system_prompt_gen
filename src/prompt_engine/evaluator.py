"""
プロンプト品質評価モジュール
生成されたプロンプトの品質を多角的に評価
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import anthropic
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """品質評価指標"""
    clarity: float = 0.0          # 明確性 (1-10)
    specificity: float = 0.0      # 具体性 (1-10)
    completeness: float = 0.0     # 完全性 (1-10)
    efficiency: float = 0.0       # 効率性 (1-10)
    reproducibility: float = 0.0  # 再現性 (1-10)
    
    def overall_score(self) -> float:
        """総合スコア計算"""
        scores = [self.clarity, self.specificity, self.completeness, 
                 self.efficiency, self.reproducibility]
        return sum(scores) / len(scores)
    
    def to_dict(self) -> Dict[str, float]:
        """辞書形式に変換"""
        return {
            'clarity': self.clarity,
            'specificity': self.specificity,
            'completeness': self.completeness,
            'efficiency': self.efficiency,
            'reproducibility': self.reproducibility,
            'overall': self.overall_score()
        }


@dataclass
class EvaluationResult:
    """評価結果"""
    metrics: QualityMetrics
    feedback: str
    suggestions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    evaluation_timestamp: str = None
    
    def __post_init__(self):
        if self.evaluation_timestamp is None:
            self.evaluation_timestamp = datetime.now().isoformat()


class PromptEvaluator:
    """プロンプト品質評価器"""
    
    def __init__(self, anthropic_client: anthropic.AsyncAnthropic,
                 model_name: str = "claude-3-sonnet-20240229"):
        self.client = anthropic_client
        self.model_name = model_name
        self.evaluation_history: List[EvaluationResult] = []
        
    async def evaluate_prompt(self, prompt_content: str, 
                             original_request: str = "",
                             context: str = "") -> EvaluationResult:
        """プロンプトの品質を評価"""
        try:
            logger.info("プロンプト品質評価開始")
            
            evaluation_prompt = self._build_evaluation_prompt(
                prompt_content, original_request, context
            )
            
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=3000,
                temperature=0.3,  # 評価は一貫性を重視
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            
            # 評価結果を解析
            result = self._parse_evaluation_response(response.content[0].text)
            
            # 履歴に追加
            self.evaluation_history.append(result)
            
            logger.info(f"品質評価完了: 総合スコア {result.metrics.overall_score():.1f}")
            return result
            
        except Exception as e:
            logger.error(f"品質評価エラー: {str(e)}")
            raise
    
    def _build_evaluation_prompt(self, prompt_content: str,
                                original_request: str = "",
                                context: str = "") -> str:
        """評価用プロンプトを構築"""
        evaluation_prompt = f"""
あなたはプロンプト品質評価の専門家です。

【評価対象プロンプト】
{prompt_content}

【元の要求】
{original_request}

【背景情報】
{context}

【評価タスク】
以下の5つの観点から1-10点で評価してください：

1. **明確性 (clarity)**: 指示の明確さと理解しやすさ
   - 曖昧さの有無
   - 指示の論理的構造
   - 用語の適切性

2. **具体性 (specificity)**: 具体的な要求の明示度
   - 詳細レベルの適切性
   - 期待値の明確性
   - 行動可能な指示

3. **完全性 (completeness)**: 必要な情報の網羅性
   - 必要な情報の不足
   - 文脈の十分性
   - 制約条件の明示

4. **効率性 (efficiency)**: トークン効率と簡潔性
   - 冗長性の除去
   - 重要情報の優先順位
   - 読みやすさ

5. **再現性 (reproducibility)**: 一貫した結果の再現性
   - 指示の一貫性
   - 結果の予測可能性
   - 品質の安定性

【出力形式】
以下のJSON形式で評価結果を出力してください：

```json
{{
  "metrics": {{
    "clarity": 8.5,
    "specificity": 7.0,
    "completeness": 9.0,
    "efficiency": 6.5,
    "reproducibility": 8.0
  }},
  "feedback": "プロンプトの強みと弱みの詳細分析（200-300文字）",
  "suggestions": [
    "具体的改善提案1",
    "具体的改善提案2", 
    "具体的改善提案3"
  ],
  "strengths": [
    "特に優れている点1",
    "特に優れている点2"
  ],
  "weaknesses": [
    "改善が必要な点1",
    "改善が必要な点2"
  ]
}}
```

JSONのみを返してください。他の説明は不要です。
"""
        return evaluation_prompt
    
    def _parse_evaluation_response(self, response_text: str) -> EvaluationResult:
        """評価レスポンスを解析"""
        try:
            # JSONブロックを抽出
            json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSONブロックがない場合は全体をJSONとして扱う
                json_str = response_text.strip()
            
            data = json.loads(json_str)
            
            # QualityMetricsオブジェクト作成
            metrics = QualityMetrics(
                clarity=data['metrics']['clarity'],
                specificity=data['metrics']['specificity'], 
                completeness=data['metrics']['completeness'],
                efficiency=data['metrics']['efficiency'],
                reproducibility=data['metrics']['reproducibility']
            )
            
            # EvaluationResultオブジェクト作成
            result = EvaluationResult(
                metrics=metrics,
                feedback=data['feedback'],
                suggestions=data['suggestions'],
                strengths=data['strengths'],
                weaknesses=data['weaknesses']
            )
            
            return result
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"評価レスポンス解析エラー: {str(e)}")
            # デフォルト評価結果を返す
            return EvaluationResult(
                metrics=QualityMetrics(
                    clarity=5.0, specificity=5.0, completeness=5.0,
                    efficiency=5.0, reproducibility=5.0
                ),
                feedback="評価結果の解析に失敗しました",
                suggestions=["評価システムの確認が必要です"],
                strengths=["不明"],
                weaknesses=["評価不可"]
            )
    
    async def batch_evaluate(self, prompts: List[Dict[str, str]]) -> List[EvaluationResult]:
        """複数プロンプトの一括評価"""
        results = []
        
        for i, prompt_data in enumerate(prompts):
            logger.info(f"一括評価進行中: {i+1}/{len(prompts)}")
            
            result = await self.evaluate_prompt(
                prompt_content=prompt_data.get('content', ''),
                original_request=prompt_data.get('request', ''),
                context=prompt_data.get('context', '')
            )
            results.append(result)
        
        logger.info(f"一括評価完了: {len(results)}件")
        return results
    
    def compare_prompts(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """複数の評価結果を比較分析"""
        if not results:
            return {"error": "比較対象の評価結果がありません"}
        
        comparison = {
            "total_prompts": len(results),
            "average_scores": {},
            "best_prompt": None,
            "worst_prompt": None,
            "improvement_areas": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 平均スコア計算
        metrics_sum = {
            'clarity': 0, 'specificity': 0, 'completeness': 0,
            'efficiency': 0, 'reproducibility': 0, 'overall': 0
        }
        
        for result in results:
            metrics_dict = result.metrics.to_dict()
            for key in metrics_sum:
                metrics_sum[key] += metrics_dict[key]
        
        for key in metrics_sum:
            comparison["average_scores"][key] = metrics_sum[key] / len(results)
        
        # 最高・最低スコアのプロンプト特定
        overall_scores = [(i, result.metrics.overall_score()) 
                         for i, result in enumerate(results)]
        overall_scores.sort(key=lambda x: x[1])
        
        comparison["worst_prompt"] = {
            "index": overall_scores[0][0],
            "score": overall_scores[0][1],
            "main_weaknesses": results[overall_scores[0][0]].weaknesses[:2]
        }
        
        comparison["best_prompt"] = {
            "index": overall_scores[-1][0],
            "score": overall_scores[-1][1],
            "main_strengths": results[overall_scores[-1][0]].strengths[:2]
        }
        
        # 改善領域の分析
        weakness_counts = {}
        for result in results:
            for weakness in result.weaknesses:
                weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        # 頻出する弱点をソート
        common_weaknesses = sorted(weakness_counts.items(), 
                                 key=lambda x: x[1], reverse=True)[:3]
        
        comparison["improvement_areas"] = {
            "common_weaknesses": common_weaknesses,
            "recommendations": [
                f"{weakness}の改善に注力する（{count}件で指摘）" 
                for weakness, count in common_weaknesses
            ]
        }
        
        return comparison
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """評価統計を取得"""
        if not self.evaluation_history:
            return {"total_evaluations": 0}
        
        stats = {
            "total_evaluations": len(self.evaluation_history),
            "average_metrics": {},
            "score_distribution": {},
            "common_strengths": {},
            "common_weaknesses": {},
            "trend_analysis": {}
        }
        
        # 平均メトリクス計算
        metrics_sum = {
            'clarity': 0, 'specificity': 0, 'completeness': 0,
            'efficiency': 0, 'reproducibility': 0, 'overall': 0
        }
        
        for result in self.evaluation_history:
            metrics_dict = result.metrics.to_dict()
            for key in metrics_sum:
                metrics_sum[key] += metrics_dict[key]
        
        for key in metrics_sum:
            stats["average_metrics"][key] = metrics_sum[key] / len(self.evaluation_history)
        
        # 強み・弱みの集計
        strength_counts = {}
        weakness_counts = {}
        
        for result in self.evaluation_history:
            for strength in result.strengths:
                strength_counts[strength] = strength_counts.get(strength, 0) + 1
            for weakness in result.weaknesses:
                weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
        
        stats["common_strengths"] = dict(sorted(strength_counts.items(), 
                                              key=lambda x: x[1], reverse=True)[:5])
        stats["common_weaknesses"] = dict(sorted(weakness_counts.items(),
                                                key=lambda x: x[1], reverse=True)[:5])
        
        return stats