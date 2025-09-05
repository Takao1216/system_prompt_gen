"""
プロンプト生成エンジンのテスト
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import anthropic

from src.prompt_engine.generator import (
    PromptGenerator,
    PromptRequest,
    PromptType,
    GeneratedPrompt
)


@pytest.fixture
def mock_anthropic_client():
    """モックAnthropic クライアント"""
    client = Mock(spec=anthropic.AsyncAnthropic)
    
    # メッセージ作成のモック
    async def mock_create(*args, **kwargs):
        mock_response = Mock()
        mock_response.content = [Mock(text="生成されたプロンプト内容")]
        return mock_response
    
    client.messages.create = AsyncMock(side_effect=mock_create)
    return client


@pytest.fixture
def prompt_generator(mock_anthropic_client):
    """プロンプトジェネレーターのフィクスチャ"""
    return PromptGenerator(mock_anthropic_client)


class TestPromptGenerator:
    """PromptGeneratorクラスのテスト"""
    
    @pytest.mark.asyncio
    async def test_generate_prompt_success(self, prompt_generator):
        """プロンプト生成が成功するケース"""
        request = PromptRequest(
            prompt_type=PromptType.DATA_ANALYSIS,
            user_requirements="売上データを分析してください",
            context="ECサイトの月次データ",
            domain="eコマース"
        )
        
        result = await prompt_generator.generate_prompt(request)
        
        assert isinstance(result, GeneratedPrompt)
        assert result.content == "生成されたプロンプト内容"
        assert result.metadata['prompt_type'] == 'data_analysis'
        assert result.metadata['domain'] == 'eコマース'
    
    @pytest.mark.asyncio
    async def test_generate_prompt_with_constraints(self, prompt_generator):
        """制約条件付きプロンプト生成"""
        request = PromptRequest(
            prompt_type=PromptType.TEXT_PROCESSING,
            user_requirements="テキストを要約してください",
            constraints=["100文字以内", "技術用語を避ける"]
        )
        
        result = await prompt_generator.generate_prompt(request)
        
        assert result.metadata['constraints_count'] == 2
    
    @pytest.mark.asyncio
    async def test_generate_prompt_with_examples(self, prompt_generator):
        """例示付きプロンプト生成"""
        request = PromptRequest(
            prompt_type=PromptType.API_TESTING,
            user_requirements="APIテストケースを作成",
            examples=["GET /users", "POST /login"]
        )
        
        result = await prompt_generator.generate_prompt(request)
        
        assert result.metadata['examples_count'] == 2
    
    @pytest.mark.asyncio
    async def test_improve_prompt_success(self, prompt_generator):
        """プロンプト改善が成功するケース"""
        original_prompt = GeneratedPrompt(
            content="元のプロンプト",
            metadata={'prompt_type': 'general_poc'}
        )
        
        feedback = "より具体的な指示が必要です"
        suggestions = ["出力形式を明確にする", "制約条件を追加する"]
        
        result = await prompt_generator.improve_prompt(
            original_prompt, feedback, suggestions
        )
        
        assert isinstance(result, GeneratedPrompt)
        assert result.content == "生成されたプロンプト内容"
        assert result.metadata.get('improvement_count') == 1
        assert result.suggestions == suggestions
    
    @pytest.mark.asyncio
    async def test_improve_prompt_multiple_iterations(self, prompt_generator):
        """複数回改善のテスト"""
        original_prompt = GeneratedPrompt(
            content="初期プロンプト",
            metadata={'prompt_type': 'data_analysis', 'improvement_count': 2}
        )
        
        result = await prompt_generator.improve_prompt(
            original_prompt, "さらなる改善が必要"
        )
        
        assert result.metadata.get('improvement_count') == 3
    
    def test_get_generation_stats_empty(self, prompt_generator):
        """統計情報（空の状態）"""
        stats = prompt_generator.get_generation_stats()
        
        assert stats['total_generations'] == 0
    
    @pytest.mark.asyncio
    async def test_get_generation_stats_with_history(self, prompt_generator):
        """統計情報（履歴あり）"""
        # いくつかプロンプトを生成
        request1 = PromptRequest(
            prompt_type=PromptType.DATA_ANALYSIS,
            user_requirements="データ分析"
        )
        request2 = PromptRequest(
            prompt_type=PromptType.IMAGE_RECOGNITION,
            user_requirements="画像認識"
        )
        
        await prompt_generator.generate_prompt(request1)
        await prompt_generator.generate_prompt(request2)
        
        stats = prompt_generator.get_generation_stats()
        
        assert stats['total_generations'] == 2
        assert 'data_analysis' in stats['by_type']
        assert 'image_recognition' in stats['by_type']
        assert stats['average_length'] > 0
        assert len(stats['recent_generations']) == 2
    
    def test_build_generation_prompt_with_all_fields(self, prompt_generator):
        """全フィールド指定時のプロンプト構築"""
        request = PromptRequest(
            prompt_type=PromptType.REQUIREMENTS_ANALYSIS,
            user_requirements="システム要件定義",
            context="新規ECサイト構築",
            domain="eコマース",
            output_format="markdown",
            constraints=["予算1000万円以内", "6ヶ月以内"],
            examples=["ユーザー登録機能", "決済機能"]
        )
        
        prompt = prompt_generator._build_generation_prompt(request)
        
        assert "システム要件定義" in prompt
        assert "新規ECサイト構築" in prompt
        assert "eコマース" in prompt
        assert "markdown" in prompt
        assert "予算1000万円以内" in prompt
        assert "ユーザー登録機能" in prompt
    
    def test_get_type_specific_instruction(self, prompt_generator):
        """タイプ別指示の取得"""
        for prompt_type in PromptType:
            instruction = prompt_generator._get_type_specific_instruction(prompt_type)
            assert isinstance(instruction, str)
            assert len(instruction) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_anthropic_client):
        """エラーハンドリングのテスト"""
        # APIエラーをシミュレート
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")
        
        generator = PromptGenerator(mock_anthropic_client)
        request = PromptRequest(
            prompt_type=PromptType.GENERAL_POC,
            user_requirements="テストリクエスト"
        )
        
        with pytest.raises(Exception) as exc_info:
            await generator.generate_prompt(request)
        
        assert "API Error" in str(exc_info.value)