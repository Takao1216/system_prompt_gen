"""
バッチ処理モジュール
複数のプロンプトを一括で生成・評価する機能を提供
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio

# Jupyter環境でのasync対応
nest_asyncio.apply()

from src.generator import PromptGenerator
from src.evaluator import PromptEvaluator
from src.prompt_history import PromptHistory


@dataclass
class BatchRequest:
    """バッチリクエストのデータクラス"""
    prompt_type: str
    user_requirements: str
    context: Optional[str] = None
    domain: Optional[str] = None
    constraints: Optional[str] = None
    

@dataclass
class BatchResult:
    """バッチ処理結果のデータクラス"""
    request: BatchRequest
    generated_prompt: str
    quality_scores: Dict[str, float]
    improved_prompt: Optional[str] = None
    processing_time: float = 0.0
    status: str = "completed"
    error: Optional[str] = None


class BatchProcessor:
    """バッチ処理クラス"""
    
    def __init__(self, 
                 generator: Optional[PromptGenerator] = None,
                 evaluator: Optional[PromptEvaluator] = None,
                 history: Optional[PromptHistory] = None,
                 max_workers: int = 3):
        """
        初期化
        
        Args:
            generator: プロンプト生成器
            evaluator: 品質評価器
            history: 履歴管理器
            max_workers: 並行処理の最大ワーカー数
        """
        self.generator = generator or PromptGenerator()
        self.evaluator = evaluator or PromptEvaluator()
        self.history = history or PromptHistory()
        self.max_workers = max_workers
        
    def process_single(self, request: BatchRequest, improve: bool = False) -> BatchResult:
        """
        単一リクエストを処理
        
        Args:
            request: バッチリクエスト
            improve: 改善処理を実行するか
            
        Returns:
            BatchResult: 処理結果
        """
        start_time = datetime.now()
        
        try:
            # プロンプト生成
            generated = self.generator.generate_prompt(
                prompt_type=request.prompt_type,
                user_requirements=request.user_requirements,
                context=request.context,
                domain=request.domain,
                constraints=request.constraints
            )
            
            # 品質評価
            scores = self.evaluator.evaluate(generated)
            
            # 改善処理（オプション）
            improved = None
            if improve and scores.get("overall", 0) < 8.0:
                improved = self.generator.improve_prompt(
                    generated,
                    self.evaluator.get_improvement_suggestions(generated, scores)
                )
                # 改善後の再評価
                scores = self.evaluator.evaluate(improved or generated)
            
            # 処理時間計算
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return BatchResult(
                request=request,
                generated_prompt=generated,
                quality_scores=scores,
                improved_prompt=improved,
                processing_time=processing_time,
                status="completed"
            )
            
        except Exception as e:
            return BatchResult(
                request=request,
                generated_prompt="",
                quality_scores={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                status="failed",
                error=str(e)
            )
    
    def process_batch(self, 
                      requests: List[BatchRequest], 
                      improve: bool = False,
                      save_history: bool = True,
                      parallel: bool = True) -> List[BatchResult]:
        """
        バッチ処理を実行
        
        Args:
            requests: バッチリクエストのリスト
            improve: 改善処理を実行するか
            save_history: 履歴に保存するか
            parallel: 並列処理を使用するか
            
        Returns:
            List[BatchResult]: 処理結果のリスト
        """
        results = []
        
        if parallel and len(requests) > 1:
            # 並列処理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self.process_single, req, improve)
                    for req in requests
                ]
                results = [future.result() for future in futures]
        else:
            # 逐次処理
            for req in requests:
                results.append(self.process_single(req, improve))
        
        # 履歴保存
        if save_history:
            for result in results:
                if result.status == "completed":
                    self.history.save_prompt(
                        prompt_type=result.request.prompt_type,
                        user_requirements=result.request.user_requirements,
                        generated_prompt=result.generated_prompt,
                        quality_scores=result.quality_scores,
                        improved_prompt=result.improved_prompt,
                        metadata={
                            "batch_processing": True,
                            "processing_time": result.processing_time,
                            "domain": result.request.domain
                        }
                    )
        
        return results
    
    async def process_batch_async(self,
                                 requests: List[BatchRequest],
                                 improve: bool = False,
                                 save_history: bool = True) -> List[BatchResult]:
        """
        非同期バッチ処理
        
        Args:
            requests: バッチリクエストのリスト
            improve: 改善処理を実行するか
            save_history: 履歴に保存するか
            
        Returns:
            List[BatchResult]: 処理結果のリスト
        """
        tasks = []
        for request in requests:
            task = asyncio.create_task(
                self._process_single_async(request, improve)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # 履歴保存
        if save_history:
            for result in results:
                if result.status == "completed":
                    self.history.save_prompt(
                        prompt_type=result.request.prompt_type,
                        user_requirements=result.request.user_requirements,
                        generated_prompt=result.generated_prompt,
                        quality_scores=result.quality_scores,
                        improved_prompt=result.improved_prompt,
                        metadata={
                            "batch_processing": True,
                            "async": True,
                            "processing_time": result.processing_time
                        }
                    )
        
        return results
    
    async def _process_single_async(self, 
                                   request: BatchRequest, 
                                   improve: bool) -> BatchResult:
        """非同期で単一リクエストを処理"""
        # 実際の処理を別スレッドで実行
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.process_single,
            request,
            improve
        )
    
    def create_batch_from_csv(self, csv_path: str) -> List[BatchRequest]:
        """
        CSVファイルからバッチリクエストを作成
        
        Args:
            csv_path: CSVファイルパス
            
        Returns:
            List[BatchRequest]: バッチリクエストのリスト
        """
        import pandas as pd
        
        df = pd.read_csv(csv_path)
        requests = []
        
        for _, row in df.iterrows():
            requests.append(BatchRequest(
                prompt_type=row.get('prompt_type', 'general'),
                user_requirements=row['user_requirements'],
                context=row.get('context'),
                domain=row.get('domain'),
                constraints=row.get('constraints')
            ))
        
        return requests
    
    def export_results(self, 
                       results: List[BatchResult], 
                       format: str = "json",
                       output_path: str = "batch_results") -> str:
        """
        バッチ処理結果をエクスポート
        
        Args:
            results: 処理結果のリスト
            format: 出力形式 (json, csv, markdown)
            output_path: 出力パス（拡張子なし）
            
        Returns:
            str: 出力ファイルパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            path = f"{output_path}_{timestamp}.json"
            data = []
            for result in results:
                data.append({
                    "prompt_type": result.request.prompt_type,
                    "user_requirements": result.request.user_requirements,
                    "generated_prompt": result.generated_prompt,
                    "quality_scores": result.quality_scores,
                    "improved_prompt": result.improved_prompt,
                    "processing_time": result.processing_time,
                    "status": result.status,
                    "error": result.error
                })
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        elif format == "csv":
            import pandas as pd
            path = f"{output_path}_{timestamp}.csv"
            
            data = []
            for result in results:
                row = {
                    "prompt_type": result.request.prompt_type,
                    "user_requirements": result.request.user_requirements,
                    "generated_prompt": result.generated_prompt[:100] + "...",
                    "overall_score": result.quality_scores.get("overall", 0),
                    "processing_time": result.processing_time,
                    "status": result.status
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(path, index=False, encoding='utf-8')
            
        elif format == "markdown":
            path = f"{output_path}_{timestamp}.md"
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write("# バッチ処理結果\\n\\n")
                f.write(f"処理日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
                f.write(f"総処理数: {len(results)}\\n\\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"## {i}. {result.request.prompt_type}\\n\\n")
                    f.write(f"**要求:** {result.request.user_requirements}\\n\\n")
                    f.write(f"**生成プロンプト:**\\n```\\n{result.generated_prompt}\\n```\\n\\n")
                    f.write(f"**品質スコア:** {result.quality_scores.get('overall', 0):.1f}/10\\n\\n")
                    f.write(f"**処理時間:** {result.processing_time:.2f}秒\\n\\n")
                    f.write("---\\n\\n")
        
        return path
    
    def get_batch_statistics(self, results: List[BatchResult]) -> Dict[str, Any]:
        """
        バッチ処理の統計情報を取得
        
        Args:
            results: 処理結果のリスト
            
        Returns:
            Dict[str, Any]: 統計情報
        """
        total = len(results)
        completed = sum(1 for r in results if r.status == "completed")
        failed = sum(1 for r in results if r.status == "failed")
        
        scores = [
            r.quality_scores.get("overall", 0) 
            for r in results 
            if r.status == "completed"
        ]
        
        processing_times = [r.processing_time for r in results]
        
        return {
            "total_requests": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "total_processing_time": sum(processing_times),
            "average_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0
        }