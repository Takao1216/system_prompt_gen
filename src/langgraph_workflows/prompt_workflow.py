"""
LangGraphを使用したプロンプト改善ワークフロー
"""

import json
from typing import Dict, List, Optional, Any, TypedDict, Annotated
from datetime import datetime
from dataclasses import dataclass
import anthropic
import logging
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from ..prompt_engine.generator import PromptGenerator, PromptRequest, PromptType
from ..prompt_engine.evaluator import PromptEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class PromptWorkflowState(TypedDict):
    """プロンプト改善ワークフローの状態"""
    
    # 基本情報
    user_request: str
    context: str
    prompt_type: str
    domain: str
    
    # プロンプト関連
    initial_prompt: str
    current_prompt: str
    improved_prompt: str
    
    # 評価結果
    quality_scores: Dict[str, float]
    evaluation_feedback: str
    improvement_suggestions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    
    # ワークフロー制御
    iteration_count: int
    max_iterations: int
    is_satisfactory: bool
    quality_threshold: float
    
    # メッセージ履歴
    messages: Annotated[List[Dict[str, str]], add_messages]
    
    # メタデータ
    workflow_start_time: str
    processing_logs: List[str]
    workflow_id: str


@dataclass
class WorkflowConfig:
    """ワークフロー設定"""
    max_iterations: int = 3
    quality_threshold: float = 8.0
    temperature: float = 0.7
    max_tokens: int = 4000
    model_name: str = "claude-3-sonnet-20240229"
    enable_logging: bool = True


class PromptImprovementWorkflow:
    """プロンプト改善ワークフロー"""
    
    def __init__(self, anthropic_client: anthropic.AsyncAnthropic, 
                 config: WorkflowConfig):
        self.client = anthropic_client
        self.config = config
        self.generator = PromptGenerator(anthropic_client, config.model_name, config.temperature)
        self.evaluator = PromptEvaluator(anthropic_client, config.model_name)
        self.workflow_history: List[PromptWorkflowState] = []
        
        # StateGraph作成
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """StateGraphを作成"""
        
        # ノード関数の定義
        async def generate_node(state: PromptWorkflowState) -> PromptWorkflowState:
            """プロンプト生成ノード"""
            try:
                if state["iteration_count"] == 0:
                    # 初回は初期プロンプト生成
                    request = PromptRequest(
                        prompt_type=PromptType(state["prompt_type"]),
                        user_requirements=state["user_request"],
                        context=state["context"],
                        domain=state["domain"]
                    )
                    
                    result = await self.generator.generate_prompt(request)
                    
                    state["initial_prompt"] = result.content
                    state["current_prompt"] = result.content
                    state["processing_logs"].append(
                        f"✅ 初期プロンプト生成完了: {len(result.content)}文字"
                    )
                else:
                    # 2回目以降は改善プロンプト生成
                    # 現在のプロンプトから GeneratedPrompt オブジェクトを作成
                    from ..prompt_engine.generator import GeneratedPrompt
                    current_generated_prompt = GeneratedPrompt(
                        content=state["current_prompt"],
                        metadata={"prompt_type": state["prompt_type"]}
                    )
                    
                    result = await self.generator.improve_prompt(
                        current_generated_prompt,
                        state["evaluation_feedback"],
                        state["improvement_suggestions"]
                    )
                    
                    state["improved_prompt"] = result.content
                    state["current_prompt"] = result.content
                    state["iteration_count"] += 1
                    state["processing_logs"].append(
                        f"🔄 プロンプト改善完了 (第{state['iteration_count']}回): {len(result.content)}文字"
                    )
                
                # メッセージ履歴更新
                state["messages"].append({
                    "role": "assistant",
                    "content": f"プロンプト生成/改善完了 (反復{state['iteration_count']}回目)"
                })
                
                return state
                
            except Exception as e:
                state["processing_logs"].append(f"❌ プロンプト生成エラー: {str(e)}")
                raise
        
        async def evaluate_node(state: PromptWorkflowState) -> PromptWorkflowState:
            """品質評価ノード"""
            try:
                result = await self.evaluator.evaluate_prompt(
                    prompt_content=state["current_prompt"],
                    original_request=state["user_request"],
                    context=state["context"]
                )
                
                # 評価結果を状態に反映
                state["quality_scores"] = result.metrics.to_dict()
                state["evaluation_feedback"] = result.feedback
                state["improvement_suggestions"] = result.suggestions
                state["strengths"] = result.strengths
                state["weaknesses"] = result.weaknesses
                
                # 品質基準達成チェック
                overall_score = result.metrics.overall_score()
                state["is_satisfactory"] = overall_score >= state["quality_threshold"]
                
                state["processing_logs"].append(
                    f"📊 品質評価完了: 総合スコア {overall_score:.1f}/10 "
                    f"({'✅ 基準達成' if state['is_satisfactory'] else '⚠️ 改善が必要'})"
                )
                
                # メッセージ履歴更新
                state["messages"].append({
                    "role": "assistant",
                    "content": f"品質評価完了: {overall_score:.1f}/10"
                })
                
                return state
                
            except Exception as e:
                state["processing_logs"].append(f"❌ 品質評価エラー: {str(e)}")
                raise
        
        def finalize_node(state: PromptWorkflowState) -> PromptWorkflowState:
            """最終化ノード"""
            final_score = state["quality_scores"].get("overall", 0)
            state["processing_logs"].append(
                f"✨ ワークフロー完了: {state['iteration_count']}回の改善, "
                f"最終スコア {final_score:.1f}/10"
            )
            
            # メッセージ履歴更新
            state["messages"].append({
                "role": "assistant",
                "content": f"ワークフロー完了: 最終スコア {final_score:.1f}/10"
            })
            
            return state
        
        def should_continue(state: PromptWorkflowState) -> str:
            """継続判定関数"""
            # 品質基準を満たしていれば終了
            if state["is_satisfactory"]:
                return "finalize"
            
            # 最大反復回数に達していれば終了
            if state["iteration_count"] >= state["max_iterations"]:
                return "finalize"
            
            return "generate"
        
        # グラフ構築
        graph = StateGraph(PromptWorkflowState)
        
        # ノード追加
        graph.add_node("generate", generate_node)
        graph.add_node("evaluate", evaluate_node)
        graph.add_node("finalize", finalize_node)
        
        # エッジ設定
        graph.set_entry_point("generate")
        graph.add_edge("generate", "evaluate")
        graph.add_conditional_edges(
            "evaluate",
            should_continue,
            {
                "generate": "generate",
                "finalize": "finalize"
            }
        )
        graph.set_finish_point("finalize")
        
        return graph
    
    def create_initial_state(self, user_request: str, context: str = "",
                           prompt_type: str = "general_poc", domain: str = "") -> PromptWorkflowState:
        """初期状態を作成"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "user_request": user_request,
            "context": context,
            "prompt_type": prompt_type,
            "domain": domain,
            "initial_prompt": "",
            "current_prompt": "",
            "improved_prompt": "",
            "quality_scores": {},
            "evaluation_feedback": "",
            "improvement_suggestions": [],
            "strengths": [],
            "weaknesses": [],
            "iteration_count": 0,
            "max_iterations": self.config.max_iterations,
            "is_satisfactory": False,
            "quality_threshold": self.config.quality_threshold,
            "messages": [],
            "workflow_start_time": datetime.now().isoformat(),
            "processing_logs": [],
            "workflow_id": workflow_id
        }
    
    async def run_workflow(self, user_request: str, context: str = "",
                          prompt_type: str = "general_poc", domain: str = "") -> PromptWorkflowState:
        """ワークフローを実行"""
        # 初期状態作成
        initial_state = self.create_initial_state(user_request, context, prompt_type, domain)
        initial_state["processing_logs"].append(f"🚀 ワークフロー開始: {initial_state['workflow_id']}")
        
        try:
            # メモリセーバー設定（チェックポイント機能）
            memory = MemorySaver()
            graph_with_memory = self.graph.compile(checkpointer=memory)
            
            # ワークフロー実行
            config = {"configurable": {"thread_id": initial_state["workflow_id"]}}
            
            final_state = None
            async for state in graph_with_memory.astream(initial_state, config):
                final_state = state
                if self.config.enable_logging:
                    logger.info(f"ワークフロー状態更新: {list(state.keys())}")
            
            if final_state is None:
                raise RuntimeError("ワークフローの実行結果が取得できませんでした")
            
            # 最終状態から実際の値を取得（LangGraphのラップを解除）
            final_workflow_state = list(final_state.values())[0]
            
            # 履歴に追加
            self.workflow_history.append(final_workflow_state)
            
            logger.info(f"ワークフロー完了: {final_workflow_state['workflow_id']}")
            return final_workflow_state
            
        except Exception as e:
            logger.error(f"ワークフロー実行エラー: {str(e)}")
            initial_state["processing_logs"].append(f"💥 ワークフロー実行エラー: {str(e)}")
            raise
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """ワークフロー統計を取得"""
        if not self.workflow_history:
            return {"total_workflows": 0}
        
        stats = {
            "total_workflows": len(self.workflow_history),
            "average_iterations": 0,
            "success_rate": 0,
            "average_final_score": 0,
            "by_prompt_type": {},
            "recent_workflows": []
        }
        
        total_iterations = 0
        successful_workflows = 0
        total_final_score = 0
        type_counts = {}
        
        for workflow in self.workflow_history:
            total_iterations += workflow["iteration_count"]
            
            if workflow["is_satisfactory"]:
                successful_workflows += 1
            
            final_score = workflow["quality_scores"].get("overall", 0)
            total_final_score += final_score
            
            prompt_type = workflow["prompt_type"]
            if prompt_type not in type_counts:
                type_counts[prompt_type] = {"count": 0, "avg_score": 0, "total_score": 0}
            
            type_counts[prompt_type]["count"] += 1
            type_counts[prompt_type]["total_score"] += final_score
        
        stats["average_iterations"] = total_iterations / len(self.workflow_history)
        stats["success_rate"] = successful_workflows / len(self.workflow_history)
        stats["average_final_score"] = total_final_score / len(self.workflow_history)
        
        # タイプ別統計
        for prompt_type, data in type_counts.items():
            stats["by_prompt_type"][prompt_type] = {
                "count": data["count"],
                "average_score": data["total_score"] / data["count"]
            }
        
        # 最近のワークフロー（最新5件）
        stats["recent_workflows"] = [
            {
                "workflow_id": workflow["workflow_id"],
                "prompt_type": workflow["prompt_type"],
                "iteration_count": workflow["iteration_count"],
                "final_score": workflow["quality_scores"].get("overall", 0),
                "is_satisfactory": workflow["is_satisfactory"],
                "start_time": workflow["workflow_start_time"]
            }
            for workflow in self.workflow_history[-5:]
        ]
        
        return stats
    
    def export_workflow_results(self, filepath: str):
        """ワークフロー結果をエクスポート"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_workflows": len(self.workflow_history),
                "config": {
                    "max_iterations": self.config.max_iterations,
                    "quality_threshold": self.config.quality_threshold,
                    "model_name": self.config.model_name
                },
                "statistics": self.get_workflow_statistics(),
                "workflows": self.workflow_history
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"ワークフロー結果をエクスポートしました: {filepath}")
            
        except Exception as e:
            logger.error(f"エクスポートエラー: {str(e)}")
            raise