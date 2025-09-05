"""
プロンプト評価器モジュール
"""

import re
from typing import Dict, List, Optional
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class PromptEvaluator:
    """プロンプト評価器クラス"""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        初期化
        
        Args:
            model: 使用するClaudeモデル名
        """
        self.model = model
        self.client = None
        
        if ANTHROPIC_AVAILABLE:
            import os
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key and api_key != "your_anthropic_api_key_here":
                self.client = anthropic.Anthropic(api_key=api_key)
        
        # 評価基準の重み
        self.weights = {
            "clarity": 0.25,
            "specificity": 0.25,
            "completeness": 0.20,
            "efficiency": 0.15,
            "reproducibility": 0.15
        }
    
    def evaluate(self, prompt: str) -> Dict[str, float]:
        """
        プロンプトを評価
        
        Args:
            prompt: 評価するプロンプト
            
        Returns:
            評価スコアの辞書
        """
        scores = {}
        
        # 明確性の評価
        scores["clarity"] = self._evaluate_clarity(prompt)
        
        # 具体性の評価
        scores["specificity"] = self._evaluate_specificity(prompt)
        
        # 完全性の評価
        scores["completeness"] = self._evaluate_completeness(prompt)
        
        # 効率性の評価
        scores["efficiency"] = self._evaluate_efficiency(prompt)
        
        # 再現可能性の評価
        scores["reproducibility"] = self._evaluate_reproducibility(prompt)
        
        # 総合スコア
        scores["overall"] = sum(
            scores[metric] * self.weights[metric] 
            for metric in self.weights
        )
        
        return scores
    
    def _evaluate_clarity(self, prompt: str) -> float:
        """明確性を評価"""
        score = 1.0
        
        # 文章の長さチェック
        sentences = prompt.split("。")
        avg_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_length > 100:
            score -= 0.2  # 文が長すぎる
        elif avg_length < 10:
            score -= 0.3  # 文が短すぎる
        
        # 構造の明確さ
        if "【" in prompt and "】" in prompt:
            score += 0.1  # 構造化されている
        
        # 箇条書きの使用
        if any(marker in prompt for marker in ["1.", "2.", "・", "-"]):
            score += 0.1  # 箇条書きで整理されている
        
        return min(max(score, 0.0), 1.0)
    
    def _evaluate_specificity(self, prompt: str) -> float:
        """具体性を評価"""
        score = 0.5
        
        # 具体的なキーワードの存在
        specific_keywords = [
            "具体的", "例えば", "以下の", "次の",
            "形式", "フォーマット", "構造", "出力"
        ]
        
        for keyword in specific_keywords:
            if keyword in prompt:
                score += 0.1
        
        # 数値や具体例の存在
        if re.search(r'\d+', prompt):
            score += 0.1
        
        # コード例やJSONの存在
        if "```" in prompt or "{" in prompt:
            score += 0.2
        
        return min(max(score, 0.0), 1.0)
    
    def _evaluate_completeness(self, prompt: str) -> float:
        """完全性を評価"""
        score = 0.3
        
        essential_elements = {
            "役割": ["あなた", "専門家", "エンジニア"],
            "タスク": ["タスク", "目的", "実行", "処理"],
            "出力": ["出力", "結果", "形式", "フォーマット"],
            "制約": ["制約", "条件", "要件", "注意"]
        }
        
        for category, keywords in essential_elements.items():
            if any(keyword in prompt for keyword in keywords):
                score += 0.15
        
        # 例示の存在
        if "例" in prompt or "Example" in prompt.lower():
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _evaluate_efficiency(self, prompt: str) -> float:
        """効率性を評価"""
        score = 0.8
        
        # 長さのペナルティ
        if len(prompt) > 2000:
            score -= 0.3  # 長すぎる
        elif len(prompt) < 50:
            score -= 0.4  # 短すぎる
        
        # 冗長な表現のチェック
        redundant_patterns = [
            r'することができ[るます]',
            r'というような',
            r'といったような'
        ]
        
        for pattern in redundant_patterns:
            if re.search(pattern, prompt):
                score -= 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _evaluate_reproducibility(self, prompt: str) -> float:
        """再現可能性を評価"""
        score = 0.5
        
        # 明確な指示の存在
        if any(word in prompt for word in ["必ず", "常に", "毎回"]):
            score += 0.2
        
        # 出力形式の明確な指定
        if "形式" in prompt or "フォーマット" in prompt:
            score += 0.2
        
        # 具体的な手順の存在
        if re.search(r'[1１][.．].*[2２][.．]', prompt):
            score += 0.2
        
        # 例示の存在
        if "例" in prompt:
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    async def evaluate_with_ai(self, prompt: str) -> Optional[Dict]:
        """
        Claude APIを使用した詳細な評価
        
        Args:
            prompt: 評価するプロンプト
            
        Returns:
            AI による評価結果
        """
        if not self.client:
            return None
        
        evaluation_prompt = """
        あなたはプロンプトエンジニアリングの専門家です。
        以下のプロンプトを評価し、JSON形式で結果を返してください。
        
        評価基準:
        1. clarity (明確性): 0-1のスコア
        2. specificity (具体性): 0-1のスコア
        3. completeness (完全性): 0-1のスコア
        4. efficiency (効率性): 0-1のスコア
        5. reproducibility (再現可能性): 0-1のスコア
        
        また、improvements（改善提案）も含めてください。
        """
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system=evaluation_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"以下のプロンプトを評価してください:\n\n{prompt}"
                    }
                ]
            )
            
            # レスポンスからJSON部分を抽出
            response_text = message.content[0].text if message.content else ""
            
            # JSON部分を抽出して解析
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return None
            
        except Exception as e:
            print(f"AI評価エラー: {e}")
            return None
    
    def get_improvement_suggestions(self, prompt: str, scores: Dict[str, float]) -> List[str]:
        """
        改善提案を生成
        
        Args:
            prompt: 評価したプロンプト
            scores: 評価スコア
            
        Returns:
            改善提案のリスト
        """
        suggestions = []
        
        # 各メトリクスに基づく提案
        if scores.get("clarity", 0) < 0.7:
            suggestions.append("文章をより簡潔に構造化し、セクションごとに明確に分けてください")
        
        if scores.get("specificity", 0) < 0.7:
            suggestions.append("より具体的な例や期待する出力形式を追加してください")
        
        if scores.get("completeness", 0) < 0.7:
            suggestions.append("役割定義、タスク説明、制約条件を明確に含めてください")
        
        if scores.get("efficiency", 0) < 0.7:
            if len(prompt) > 1500:
                suggestions.append("プロンプトを簡潔にし、冗長な部分を削除してください")
            else:
                suggestions.append("必要な情報をより効率的に伝える構成を検討してください")
        
        if scores.get("reproducibility", 0) < 0.7:
            suggestions.append("出力形式の明確な指定と具体例を追加してください")
        
        return suggestions