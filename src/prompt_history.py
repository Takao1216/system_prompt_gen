"""
プロンプト履歴管理モジュール
生成したプロンプトの保存、検索、再利用機能を提供
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class PromptHistory:
    """プロンプト履歴管理クラス"""
    
    def __init__(self, history_dir: str = "prompt_history"):
        """
        初期化
        
        Args:
            history_dir (str): 履歴保存ディレクトリ
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.history_file = self.history_dir / "prompts.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """履歴ファイルを読み込み"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self) -> None:
        """履歴をファイルに保存"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """プロンプトのユニークIDを生成"""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    
    def save_prompt(
        self,
        prompt_type: str,
        user_requirements: str,
        generated_prompt: str,
        quality_scores: Optional[Dict[str, float]] = None,
        improved_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        プロンプトを履歴に保存
        
        Args:
            prompt_type (str): プロンプトタイプ
            user_requirements (str): ユーザー要求
            generated_prompt (str): 生成されたプロンプト
            quality_scores (Optional[Dict[str, float]]): 品質スコア
            improved_prompt (Optional[str]): 改善後のプロンプト
            metadata (Optional[Dict[str, Any]]): その他メタデータ
            
        Returns:
            str: 保存したプロンプトのID
        """
        prompt_id = self._generate_id(generated_prompt)
        
        entry = {
            "id": prompt_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_type": prompt_type,
            "user_requirements": user_requirements,
            "generated_prompt": generated_prompt,
            "quality_scores": quality_scores or {},
            "improved_prompt": improved_prompt,
            "metadata": metadata or {},
            "tags": self._extract_tags(user_requirements)
        }
        
        self.history.append(entry)
        self._save_history()
        
        return prompt_id
    
    def _extract_tags(self, text: str) -> List[str]:
        """テキストからタグを自動抽出"""
        # 簡易的なタグ抽出（将来的にNLPで改善可能）
        tags = []
        keywords = ["データ分析", "画像認識", "テキスト処理", "API", "テスト", "要件定義"]
        for keyword in keywords:
            if keyword in text:
                tags.append(keyword)
        return tags
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        IDでプロンプトを取得
        
        Args:
            prompt_id (str): プロンプトID
            
        Returns:
            Optional[Dict[str, Any]]: プロンプト情報
        """
        for entry in self.history:
            if entry["id"] == prompt_id:
                return entry
        return None
    
    def search_prompts(
        self,
        prompt_type: Optional[str] = None,
        keyword: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        条件に基づいてプロンプトを検索
        
        Args:
            prompt_type (Optional[str]): プロンプトタイプでフィルタ
            keyword (Optional[str]): キーワード検索
            tags (Optional[List[str]]): タグでフィルタ
            min_score (Optional[float]): 最小品質スコア
            
        Returns:
            List[Dict[str, Any]]: 検索結果
        """
        results = self.history.copy()
        
        # プロンプトタイプでフィルタ
        if prompt_type:
            results = [r for r in results if r["prompt_type"] == prompt_type]
        
        # キーワード検索
        if keyword:
            keyword_lower = keyword.lower()
            results = [
                r for r in results
                if keyword_lower in r["user_requirements"].lower()
                or keyword_lower in r["generated_prompt"].lower()
            ]
        
        # タグでフィルタ
        if tags:
            results = [
                r for r in results
                if any(tag in r.get("tags", []) for tag in tags)
            ]
        
        # 品質スコアでフィルタ
        if min_score is not None:
            results = [
                r for r in results
                if r.get("quality_scores", {}).get("overall", 0) >= min_score
            ]
        
        # タイムスタンプで降順ソート
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return results
    
    def get_recent_prompts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        最近のプロンプトを取得
        
        Args:
            limit (int): 取得件数
            
        Returns:
            List[Dict[str, Any]]: 最近のプロンプト
        """
        return self.history[-limit:][::-1]
    
    def get_best_prompts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        高評価のプロンプトを取得
        
        Args:
            limit (int): 取得件数
            
        Returns:
            List[Dict[str, Any]]: 高評価プロンプト
        """
        scored_prompts = [
            p for p in self.history
            if p.get("quality_scores", {}).get("overall")
        ]
        scored_prompts.sort(
            key=lambda x: x["quality_scores"]["overall"],
            reverse=True
        )
        return scored_prompts[:limit]
    
    def export_history(self, export_path: str = "prompt_history_export.json") -> str:
        """
        履歴をエクスポート
        
        Args:
            export_path (str): エクスポート先パス
            
        Returns:
            str: エクスポートファイルパス
        """
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_prompts": len(self.history),
            "prompts": self.history
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return export_path
    
    def import_history(self, import_path: str) -> int:
        """
        履歴をインポート
        
        Args:
            import_path (str): インポート元パス
            
        Returns:
            int: インポートしたプロンプト数
        """
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        imported_prompts = import_data.get("prompts", [])
        
        # 重複チェック（IDベース）
        existing_ids = {p["id"] for p in self.history}
        new_prompts = [
            p for p in imported_prompts
            if p["id"] not in existing_ids
        ]
        
        self.history.extend(new_prompts)
        self._save_history()
        
        return len(new_prompts)
    
    def clear_history(self) -> None:
        """履歴をクリア"""
        self.history = []
        self._save_history()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        履歴の統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        if not self.history:
            return {
                "total_prompts": 0,
                "prompt_types": {},
                "average_score": 0,
                "best_score": 0,
                "most_used_tags": []
            }
        
        # プロンプトタイプ別カウント
        type_counts = {}
        for entry in self.history:
            ptype = entry["prompt_type"]
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        # 品質スコア統計
        scores = [
            entry["quality_scores"].get("overall", 0)
            for entry in self.history
            if entry.get("quality_scores", {}).get("overall")
        ]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        # タグ統計
        tag_counts = {}
        for entry in self.history:
            for tag in entry.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_used_tags = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_prompts": len(self.history),
            "prompt_types": type_counts,
            "average_score": round(avg_score, 2),
            "best_score": round(best_score, 2),
            "most_used_tags": [tag for tag, _ in most_used_tags]
        }