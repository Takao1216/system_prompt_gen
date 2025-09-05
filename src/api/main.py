"""
FastAPI メインアプリケーション
プロンプト生成システムのWeb APIエンドポイント
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import anthropic

from ..prompt_engine.generator import PromptGenerator, PromptRequest, PromptType, GeneratedPrompt
from ..prompt_engine.evaluator import PromptEvaluator
from ..langgraph_workflows.prompt_workflow import PromptImprovementWorkflow, WorkflowConfig

# 環境変数読み込み
load_dotenv()

# ログ設定
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# グローバル変数
anthropic_client = None
prompt_generator = None
prompt_evaluator = None
workflow = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    global anthropic_client, prompt_generator, prompt_evaluator, workflow
    
    # 起動時の初期化
    logger.info("Initializing application...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables")
        raise ValueError("ANTHROPIC_API_KEY is required")
    
    anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
    
    # 各コンポーネント初期化
    model_name = os.getenv('DEFAULT_MODEL', 'claude-3-sonnet-20240229')
    prompt_generator = PromptGenerator(anthropic_client, model_name)
    prompt_evaluator = PromptEvaluator(anthropic_client, model_name)
    
    workflow_config = WorkflowConfig(
        max_iterations=3,
        quality_threshold=8.0,
        temperature=float(os.getenv('TEMPERATURE', '0.7')),
        max_tokens=int(os.getenv('MAX_TOKENS', '4000')),
        model_name=model_name
    )
    workflow = PromptImprovementWorkflow(anthropic_client, workflow_config)
    
    logger.info("Application initialized successfully")
    
    yield
    
    # シャットダウン時のクリーンアップ
    logger.info("Shutting down application...")


# FastAPIアプリケーション作成
app = FastAPI(
    title="プロンプト生成システム API",
    description="AIエンジニア向けPoC開発支援プロンプト生成システム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# リクエスト/レスポンスモデル定義
class PromptGenerationRequest(BaseModel):
    """プロンプト生成リクエスト"""
    prompt_type: str = "general_poc"
    user_requirements: str
    context: str = ""
    domain: str = ""
    output_format: str = "structured"
    constraints: List[str] = []
    examples: List[str] = []


class PromptGenerationResponse(BaseModel):
    """プロンプト生成レスポンス"""
    success: bool
    prompt: str
    metadata: Dict[str, Any]
    quality_score: float = 0.0
    suggestions: List[str] = []
    created_at: str
    error: Optional[str] = None


class PromptEvaluationRequest(BaseModel):
    """プロンプト評価リクエスト"""
    prompt_content: str
    original_request: str = ""
    context: str = ""


class PromptEvaluationResponse(BaseModel):
    """プロンプト評価レスポンス"""
    success: bool
    quality_scores: Dict[str, float]
    feedback: str
    suggestions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    evaluation_timestamp: str
    error: Optional[str] = None


class WorkflowRequest(BaseModel):
    """ワークフロー実行リクエスト"""
    user_request: str
    context: str = ""
    prompt_type: str = "general_poc"
    domain: str = ""


class WorkflowResponse(BaseModel):
    """ワークフロー実行レスポンス"""
    success: bool
    workflow_id: str
    final_prompt: str
    quality_scores: Dict[str, float]
    iteration_count: int
    is_satisfactory: bool
    processing_logs: List[str]
    error: Optional[str] = None


# APIエンドポイント
@app.get("/", response_class=HTMLResponse)
async def root():
    """ルートエンドポイント - API概要ページ"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>プロンプト生成システム API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #007bff; }
            .path { color: #28a745; }
        </style>
    </head>
    <body>
        <h1>🚀 プロンプト生成システム API</h1>
        <p>AIエンジニア向けPoC開発支援プロンプト生成システムのAPIです。</p>
        
        <h2>利用可能なエンドポイント</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/health</span>
            <p>ヘルスチェックエンドポイント</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/v1/generate</span>
            <p>プロンプト生成</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/v1/evaluate</span>
            <p>プロンプト品質評価</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/v1/workflow</span>
            <p>自動改善ワークフロー実行</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/v1/prompt-types</span>
            <p>利用可能なプロンプトタイプ一覧</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/v1/statistics</span>
            <p>システム統計情報</p>
        </div>
        
        <h2>ドキュメント</h2>
        <ul>
            <li><a href="/docs">Swagger UI (対話的API文書)</a></li>
            <li><a href="/redoc">ReDoc (API仕様書)</a></li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "anthropic_client": anthropic_client is not None,
            "prompt_generator": prompt_generator is not None,
            "prompt_evaluator": prompt_evaluator is not None,
            "workflow": workflow is not None
        }
    }


@app.post("/api/v1/generate", response_model=PromptGenerationResponse)
async def generate_prompt(request: PromptGenerationRequest):
    """プロンプト生成エンドポイント"""
    try:
        # PromptRequestオブジェクト作成
        prompt_request = PromptRequest(
            prompt_type=PromptType(request.prompt_type),
            user_requirements=request.user_requirements,
            context=request.context,
            domain=request.domain,
            output_format=request.output_format,
            constraints=request.constraints,
            examples=request.examples
        )
        
        # プロンプト生成
        result = await prompt_generator.generate_prompt(prompt_request)
        
        return PromptGenerationResponse(
            success=True,
            prompt=result.content,
            metadata=result.metadata,
            quality_score=result.quality_score,
            suggestions=result.suggestions,
            created_at=result.created_at
        )
        
    except Exception as e:
        logger.error(f"プロンプト生成エラー: {str(e)}")
        return PromptGenerationResponse(
            success=False,
            prompt="",
            metadata={},
            created_at=datetime.now().isoformat(),
            error=str(e)
        )


@app.post("/api/v1/evaluate", response_model=PromptEvaluationResponse)
async def evaluate_prompt(request: PromptEvaluationRequest):
    """プロンプト評価エンドポイント"""
    try:
        # プロンプト評価実行
        result = await prompt_evaluator.evaluate_prompt(
            prompt_content=request.prompt_content,
            original_request=request.original_request,
            context=request.context
        )
        
        return PromptEvaluationResponse(
            success=True,
            quality_scores=result.metrics.to_dict(),
            feedback=result.feedback,
            suggestions=result.suggestions,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            evaluation_timestamp=result.evaluation_timestamp
        )
        
    except Exception as e:
        logger.error(f"プロンプト評価エラー: {str(e)}")
        return PromptEvaluationResponse(
            success=False,
            quality_scores={},
            feedback="",
            suggestions=[],
            strengths=[],
            weaknesses=[],
            evaluation_timestamp=datetime.now().isoformat(),
            error=str(e)
        )


@app.post("/api/v1/workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """自動改善ワークフロー実行エンドポイント"""
    try:
        # ワークフロー実行
        result = await workflow.run_workflow(
            user_request=request.user_request,
            context=request.context,
            prompt_type=request.prompt_type,
            domain=request.domain
        )
        
        return WorkflowResponse(
            success=True,
            workflow_id=result["workflow_id"],
            final_prompt=result["current_prompt"],
            quality_scores=result["quality_scores"],
            iteration_count=result["iteration_count"],
            is_satisfactory=result["is_satisfactory"],
            processing_logs=result["processing_logs"]
        )
        
    except Exception as e:
        logger.error(f"ワークフロー実行エラー: {str(e)}")
        return WorkflowResponse(
            success=False,
            workflow_id="",
            final_prompt="",
            quality_scores={},
            iteration_count=0,
            is_satisfactory=False,
            processing_logs=[],
            error=str(e)
        )


@app.get("/api/v1/prompt-types")
async def get_prompt_types():
    """利用可能なプロンプトタイプ一覧"""
    return {
        "prompt_types": [
            {
                "value": pt.value,
                "name": pt.name,
                "description": {
                    "data_analysis": "データ分析・可視化プロンプト",
                    "image_recognition": "画像認識・分類プロンプト",
                    "text_processing": "テキスト処理・NLPプロンプト",
                    "requirements_analysis": "要件定義支援プロンプト",
                    "api_testing": "APIテスト用プロンプト",
                    "general_poc": "汎用PoC用プロンプト"
                }.get(pt.value, "")
            }
            for pt in PromptType
        ]
    }


@app.get("/api/v1/statistics")
async def get_statistics():
    """システム統計情報"""
    try:
        generator_stats = prompt_generator.get_generation_stats() if prompt_generator else {}
        evaluator_stats = prompt_evaluator.get_evaluation_statistics() if prompt_evaluator else {}
        workflow_stats = workflow.get_workflow_statistics() if workflow else {}
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "generation": generator_stats,
                "evaluation": evaluator_stats,
                "workflow": workflow_stats
            }
        }
        
    except Exception as e:
        logger.error(f"統計情報取得エラー: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "statistics": {}
        }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('APP_HOST', 'localhost')
    port = int(os.getenv('APP_PORT', '8000'))
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=os.getenv('DEBUG_MODE', 'true').lower() == 'true'
    )