"""
プロンプト品質評価モジュールのテスト
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock
import anthropic

from src.prompt_engine.evaluator import (
    PromptEvaluator,
    QualityMetrics,
    EvaluationResult
)


@pytest.fixture
def mock_anthropic_client():
    """モックAnthropic クライアント"""
    client = Mock(spec=anthropic.AsyncAnthropic)
    
    # デフォルトの評価レスポンス
    default_response = {
        "metrics": {
            "clarity": 8.5,
            "specificity": 7.0,
            "completeness": 9.0,
            "efficiency": 6.5,
            "reproducibility": 8.0
        },
        "feedback": "プロンプトは明確で具体的ですが、効率性に改善の余地があります",
        "suggestions": [
            "より簡潔な表現を使用する",
            "冗長な説明を削除する",
            "出力形式をより具体的に指定する"
        ],
        "strengths": [
            "指示が明確である",
            "必要な情報が網羅されている"
        ],
        "weaknesses": [
            "やや冗長な表現がある",
            "トークン効率が低い"
        ]
    }
    
    async def mock_create(*args, **kwargs):
        mock_response = Mock()
        mock_response.content = [Mock(text=f"```json\n{json.dumps(default_response)}\n```")]
        return mock_response
    
    client.messages.create = AsyncMock(side_effect=mock_create)
    return client


@pytest.fixture
def prompt_evaluator(mock_anthropic_client):
    """プロンプト評価器のフィクスチャ"""
    return PromptEvaluator(mock_anthropic_client)


class TestQualityMetrics:
    """QualityMetricsクラスのテスト"""
    
    def test_overall_score_calculation(self):
        """総合スコア計算のテスト"""
        metrics = QualityMetrics(
            clarity=8.0,
            specificity=7.5,
            completeness=9.0,
            efficiency=6.0,
            reproducibility=8.5
        )
        
        expected_score = (8.0 + 7.5 + 9.0 + 6.0 + 8.5) / 5
        assert metrics.overall_score() == expected_score
    
    def test_to_dict_conversion(self):
        """辞書変換のテスト"""
        metrics = QualityMetrics(
            clarity=8.0,
            specificity=7.0,
            completeness=9.0,
            efficiency=6.0,
            reproducibility=8.0
        )
        
        result = metrics.to_dict()
        
        assert result['clarity'] == 8.0
        assert result['specificity'] == 7.0
        assert result['completeness'] == 9.0
        assert result['efficiency'] == 6.0
        assert result['reproducibility'] == 8.0
        assert 'overall' in result


class TestPromptEvaluator:
    """PromptEvaluatorクラスのテスト"""
    
    @pytest.mark.asyncio
    async def test_evaluate_prompt_success(self, prompt_evaluator):
        """プロンプト評価が成功するケース"""
        result = await prompt_evaluator.evaluate_prompt(
            prompt_content="テスト用プロンプト",
            original_request="データ分析をしてください",
            context="売上データの分析"
        )
        
        assert isinstance(result, EvaluationResult)
        assert isinstance(result.metrics, QualityMetrics)
        assert result.metrics.clarity == 8.5
        assert result.metrics.specificity == 7.0
        assert len(result.suggestions) == 3
        assert len(result.strengths) == 2
        assert len(result.weaknesses) == 2
    
    @pytest.mark.asyncio
    async def test_evaluate_prompt_minimal_input(self, prompt_evaluator):
        """最小入力での評価"""
        result = await prompt_evaluator.evaluate_prompt(
            prompt_content="シンプルなプロンプト"
        )
        
        assert isinstance(result, EvaluationResult)
        assert result.evaluation_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_parse_evaluation_response_valid_json(self, prompt_evaluator):
        """有効なJSONレスポンスの解析"""
        json_response = '''```json
        {
            "metrics": {
                "clarity": 9.0,
                "specificity": 8.5,
                "completeness": 9.5,
                "efficiency": 7.0,
                "reproducibility": 8.5
            },
            "feedback": "優れたプロンプトです",
            "suggestions": ["特になし"],
            "strengths": ["完全性が高い"],
            "weaknesses": ["効率性に改善余地"]
        }
        ```'''
        
        result = prompt_evaluator._parse_evaluation_response(json_response)
        
        assert result.metrics.clarity == 9.0
        assert result.metrics.completeness == 9.5
        assert result.feedback == "優れたプロンプトです"
    
    @pytest.mark.asyncio
    async def test_parse_evaluation_response_invalid_json(self, prompt_evaluator):
        """無効なJSONレスポンスの処理"""
        invalid_response = "これは有効なJSONではありません"
        
        result = prompt_evaluator._parse_evaluation_response(invalid_response)
        
        # デフォルト値が設定されることを確認
        assert result.metrics.clarity == 5.0
        assert result.metrics.specificity == 5.0
        assert result.feedback == "評価結果の解析に失敗しました"
        assert "評価システムの確認が必要です" in result.suggestions
    
    @pytest.mark.asyncio
    async def test_batch_evaluate(self, prompt_evaluator):
        """複数プロンプトの一括評価"""
        prompts = [
            {
                'content': 'プロンプト1',
                'request': '要求1',
                'context': '文脈1'
            },
            {
                'content': 'プロンプト2',
                'request': '要求2',
                'context': '文脈2'
            },
            {
                'content': 'プロンプト3',
                'request': '要求3',
                'context': '文脈3'
            }
        ]
        
        results = await prompt_evaluator.batch_evaluate(prompts)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, EvaluationResult)
            assert isinstance(result.metrics, QualityMetrics)
    
    def test_compare_prompts(self, prompt_evaluator):
        """プロンプト比較分析"""
        # テスト用の評価結果を作成
        results = [
            EvaluationResult(
                metrics=QualityMetrics(8, 7, 9, 6, 8),
                feedback="良好",
                suggestions=["改善1"],
                strengths=["強み1"],
                weaknesses=["弱点1", "弱点共通"]
            ),
            EvaluationResult(
                metrics=QualityMetrics(9, 8, 8, 7, 9),
                feedback="優秀",
                suggestions=["改善2"],
                strengths=["強み2"],
                weaknesses=["弱点2", "弱点共通"]
            ),
            EvaluationResult(
                metrics=QualityMetrics(6, 6, 7, 5, 6),
                feedback="要改善",
                suggestions=["改善3"],
                strengths=["強み3"],
                weaknesses=["弱点3", "弱点共通"]
            )
        ]
        
        comparison = prompt_evaluator.compare_prompts(results)
        
        assert comparison['total_prompts'] == 3
        assert 'average_scores' in comparison
        assert 'best_prompt' in comparison
        assert 'worst_prompt' in comparison
        assert comparison['best_prompt']['index'] == 1  # 2番目が最高スコア
        assert comparison['worst_prompt']['index'] == 2  # 3番目が最低スコア
        assert len(comparison['improvement_areas']['common_weaknesses']) <= 3
    
    def test_compare_prompts_empty(self, prompt_evaluator):
        """空のリストでの比較"""
        comparison = prompt_evaluator.compare_prompts([])
        
        assert 'error' in comparison
        assert comparison['error'] == "比較対象の評価結果がありません"
    
    def test_get_evaluation_statistics_empty(self, prompt_evaluator):
        """評価統計（空の状態）"""
        stats = prompt_evaluator.get_evaluation_statistics()
        
        assert stats['total_evaluations'] == 0
    
    @pytest.mark.asyncio
    async def test_get_evaluation_statistics_with_history(self, prompt_evaluator):
        """評価統計（履歴あり）"""
        # いくつか評価を実行
        await prompt_evaluator.evaluate_prompt("プロンプト1")
        await prompt_evaluator.evaluate_prompt("プロンプト2")
        
        stats = prompt_evaluator.get_evaluation_statistics()
        
        assert stats['total_evaluations'] == 2
        assert 'average_metrics' in stats
        assert 'common_strengths' in stats
        assert 'common_weaknesses' in stats
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_anthropic_client):
        """エラーハンドリングのテスト"""
        # APIエラーをシミュレート
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")
        
        evaluator = PromptEvaluator(mock_anthropic_client)
        
        with pytest.raises(Exception) as exc_info:
            await evaluator.evaluate_prompt("テストプロンプト")
        
        assert "API Error" in str(exc_info.value)
    
    def test_build_evaluation_prompt(self, prompt_evaluator):
        """評価用プロンプト構築のテスト"""
        evaluation_prompt = prompt_evaluator._build_evaluation_prompt(
            prompt_content="テストプロンプト",
            original_request="元の要求",
            context="背景情報"
        )
        
        assert "テストプロンプト" in evaluation_prompt
        assert "元の要求" in evaluation_prompt
        assert "背景情報" in evaluation_prompt
        assert "clarity" in evaluation_prompt
        assert "specificity" in evaluation_prompt
        assert "completeness" in evaluation_prompt
        assert "efficiency" in evaluation_prompt
        assert "reproducibility" in evaluation_prompt