"""
プロンプトテンプレート管理システム
事前定義済みテンプレートの管理とカスタムテンプレート作成
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """プロンプトテンプレート"""
    id: str
    name: str
    category: str
    description: str
    template_content: str
    variables: List[str]
    tags: List[str]
    created_at: str
    updated_at: str
    usage_count: int = 0
    is_custom: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'template_content': self.template_content,
            'variables': self.variables,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'usage_count': self.usage_count,
            'is_custom': self.is_custom
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """辞書からインスタンス作成"""
        return cls(**data)


class TemplateManager:
    """テンプレート管理クラス"""
    
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        self.templates_file = self.templates_dir / 'templates.json'
        self.custom_templates_file = self.templates_dir / 'custom_templates.json'
        
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
        self._load_custom_templates()
    
    def _load_default_templates(self):
        """デフォルトテンプレートを読み込み"""
        default_templates = self._get_default_templates()
        
        for template_data in default_templates:
            template = PromptTemplate(**template_data)
            self.templates[template.id] = template
        
        logger.info(f"デフォルトテンプレート {len(default_templates)}個を読み込みました")
    
    def _get_default_templates(self) -> List[Dict[str, Any]]:
        """デフォルトテンプレートの定義"""
        timestamp = datetime.now().isoformat()
        
        return [
            {
                'id': 'data_analysis_poc',
                'name': 'データ分析PoC',
                'category': 'data_analysis',
                'description': 'データ分析プロジェクト用のプロンプトテンプレート',
                'template_content': '''
あなたは経験豊富なデータサイエンティストです。

【分析対象】
{data_description}

【分析目的】
{analysis_objective}

【利用可能なデータ】
{available_data}

【期待する分析手法】
{analysis_methods}

【出力要件】
1. エグゼクティブサマリー（要点を3点以内）
2. 主要な発見事項（統計値を含む）
3. データの可視化提案（グラフタイプと内容）
4. ビジネス影響の評価
5. 次のアクションプラン

【制約条件】
{constraints}
- 統計的有意性を必ず検証すること
- ビジネス担当者にも理解できる平易な説明を含めること

分析を開始してください。
                '''.strip(),
                'variables': [
                    'data_description',
                    'analysis_objective',
                    'available_data',
                    'analysis_methods',
                    'constraints'
                ],
                'tags': ['data', 'analysis', 'poc', 'statistics'],
                'created_at': timestamp,
                'updated_at': timestamp,
                'usage_count': 0,
                'is_custom': False
            },
            {
                'id': 'image_recognition_poc',
                'name': '画像認識PoC',
                'category': 'image_recognition',
                'description': '画像認識プロジェクト用のプロンプトテンプレート',
                'template_content': '''
あなたはコンピュータビジョンの専門家です。

【対象画像】
{image_types}

【認識タスク】
{recognition_task}

【認識対象】
{target_objects}

【精度要件】
{accuracy_requirements}

【利用環境】
{deployment_environment}

【出力形式】
```json
{
  "detected_objects": [
    {
      "class": "オブジェクト名",
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "processing_time": "実行時間（秒）",
  "model_info": "使用モデル情報"
}
```

【制約条件】
{constraints}
- リアルタイム処理要件を考慮すること
- 誤検出の処理方法を明確にすること

画像認識を実行してください。
                '''.strip(),
                'variables': [
                    'image_types',
                    'recognition_task',
                    'target_objects',
                    'accuracy_requirements',
                    'deployment_environment',
                    'constraints'
                ],
                'tags': ['image', 'recognition', 'computer_vision', 'poc'],
                'created_at': timestamp,
                'updated_at': timestamp,
                'usage_count': 0,
                'is_custom': False
            },
            {
                'id': 'text_processing_poc',
                'name': 'テキスト処理PoC',
                'category': 'text_processing',
                'description': '自然言語処理プロジェクト用のプロンプトテンプレート',
                'template_content': '''
あなたは自然言語処理の専門家です。

【処理対象テキスト】
{text_type}: {text_description}

【処理タスク】
{processing_tasks}

【処理要件】
{processing_requirements}

【品質基準】
{quality_criteria}

【出力言語・文体】
{language_style}

【出力構造】
```json
{
  "original_text": "元テキスト（抜粋）",
  "processing_results": {
    "task1": "結果1",
    "task2": "結果2"
  },
  "confidence_scores": {
    "task1": 0.92,
    "task2": 0.88
  },
  "processing_notes": "処理時の注意点や課題"
}
```

【制約条件】
{constraints}
- 文脈の理解を重視すること
- あいまいな表現は適切に解釈すること

テキスト処理を開始してください。
                '''.strip(),
                'variables': [
                    'text_type',
                    'text_description',
                    'processing_tasks',
                    'processing_requirements',
                    'quality_criteria',
                    'language_style',
                    'constraints'
                ],
                'tags': ['nlp', 'text', 'processing', 'poc'],
                'created_at': timestamp,
                'updated_at': timestamp,
                'usage_count': 0,
                'is_custom': False
            },
            {
                'id': 'requirements_analysis_poc',
                'name': '要件定義支援',
                'category': 'requirements_analysis',
                'description': 'システム要件定義のためのプロンプトテンプレート',
                'template_content': '''
あなたはシステムアナリストとして、要件定義を支援してください。

【対象システム】
{system_description}

【ステークホルダー】
{stakeholders}

【ビジネス背景】
{business_context}

【現状の課題】
{current_issues}

【期待する効果】
{expected_benefits}

【制約条件】
{constraints}

【要求事項】
1. **機能要件**
   - 必須機能（MustHave）
   - 重要機能（ShouldHave）
   - あると良い機能（CouldHave）

2. **非機能要件**
   - 性能要件
   - セキュリティ要件
   - 可用性・信頼性要件

3. **技術要件**
   - アーキテクチャ方針
   - インフラ要件

4. **リスク分析**
   - 技術的リスク
   - スケジュールリスク

各要件には優先度と実現難易度を含めてください。
                '''.strip(),
                'variables': [
                    'system_description',
                    'stakeholders',
                    'business_context',
                    'current_issues',
                    'expected_benefits',
                    'constraints'
                ],
                'tags': ['requirements', 'analysis', 'system', 'poc'],
                'created_at': timestamp,
                'updated_at': timestamp,
                'usage_count': 0,
                'is_custom': False
            },
            {
                'id': 'api_testing_poc',
                'name': 'APIテスト',
                'category': 'api_testing',
                'description': 'API機能テスト用のプロンプトテンプレート',
                'template_content': '''
あなたはAPIテストの専門家です。

【対象API】
{api_endpoint}: {api_description}

【テスト観点】
{test_scenarios}

【期待する品質】
{quality_requirements}

【環境情報】
{environment_info}

【テストケース作成】
以下の観点でテストケースを作成してください：

1. **正常系テスト**
   - 基本的な成功シナリオ
   - パラメータ組み合わせ

2. **異常系テスト**
   - エラーハンドリング
   - 不正な入力

3. **境界値テスト**
   - 最大値・最小値
   - 特殊文字

4. **セキュリティテスト**
   - 認証・認可
   - インジェクション対策

各テストケースには、入力データ、期待結果、検証ポイントを含めてください。
                '''.strip(),
                'variables': [
                    'api_endpoint',
                    'api_description',
                    'test_scenarios',
                    'quality_requirements',
                    'environment_info'
                ],
                'tags': ['api', 'testing', 'qa', 'poc'],
                'created_at': timestamp,
                'updated_at': timestamp,
                'usage_count': 0,
                'is_custom': False
            }
        ]
    
    def _load_custom_templates(self):
        """カスタムテンプレートを読み込み"""
        if self.custom_templates_file.exists():
            try:
                with open(self.custom_templates_file, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                    for template_data in custom_data:
                        template = PromptTemplate.from_dict(template_data)
                        self.templates[template.id] = template
                    logger.info(f"カスタムテンプレート {len(custom_data)}個を読み込みました")
            except Exception as e:
                logger.warning(f"カスタムテンプレート読み込みエラー: {str(e)}")
    
    def save_custom_templates(self):
        """カスタムテンプレートを保存"""
        custom_templates = [
            template.to_dict()
            for template in self.templates.values()
            if template.is_custom
        ]
        
        try:
            with open(self.custom_templates_file, 'w', encoding='utf-8') as f:
                json.dump(custom_templates, f, indent=2, ensure_ascii=False)
            logger.info(f"カスタムテンプレート {len(custom_templates)}個を保存しました")
        except Exception as e:
            logger.error(f"カスタムテンプレート保存エラー: {str(e)}")
            raise
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """テンプレートを取得"""
        # IDで検索
        if template_id in self.templates:
            return self.templates[template_id]
        
        # カテゴリ名でも検索できるように
        for tid, template in self.templates.items():
            if template.category == template_id:
                return template
        
        return None
    
    def list_templates(self, category: str = None, tags: List[str] = None) -> List[PromptTemplate]:
        """テンプレート一覧を取得"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]
        
        return templates
    
    def add_custom_template(self, name: str, category: str, description: str,
                           template_content: str, variables: List[str],
                           tags: List[str] = None) -> PromptTemplate:
        """カスタムテンプレートを追加"""
        if tags is None:
            tags = []
        
        timestamp = datetime.now().isoformat()
        template_id = f"custom_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        template = PromptTemplate(
            id=template_id,
            name=name,
            category=category,
            description=description,
            template_content=template_content,
            variables=variables,
            tags=tags,
            created_at=timestamp,
            updated_at=timestamp,
            usage_count=0,
            is_custom=True
        )
        
        self.templates[template_id] = template
        self.save_custom_templates()
        
        logger.info(f"カスタムテンプレート '{name}' を追加しました")
        return template
    
    def update_template(self, template_id: str, **updates) -> Optional[PromptTemplate]:
        """テンプレートを更新"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        if not template.is_custom:
            logger.warning(f"デフォルトテンプレート '{template_id}' は更新できません")
            return None
        
        # 更新可能なフィールドのみ更新
        updatable_fields = ['name', 'description', 'template_content', 'variables', 'tags']
        for field, value in updates.items():
            if field in updatable_fields and value is not None:
                setattr(template, field, value)
        
        template.updated_at = datetime.now().isoformat()
        self.save_custom_templates()
        
        logger.info(f"テンプレート '{template_id}' を更新しました")
        return template
    
    def delete_custom_template(self, template_id: str) -> bool:
        """カスタムテンプレートを削除"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        if not template.is_custom:
            logger.warning(f"デフォルトテンプレート '{template_id}' は削除できません")
            return False
        
        del self.templates[template_id]
        self.save_custom_templates()
        
        logger.info(f"テンプレート '{template_id}' を削除しました")
        return True
    
    def generate_prompt(self, template_id: str, variables: Dict[str, str]) -> Optional[str]:
        """テンプレートから具体的なプロンプトを生成"""
        template = self.get_template(template_id)
        if not template:
            logger.error(f"テンプレート '{template_id}' が見つかりません")
            return None
        
        # 必要な変数の確認
        required_vars = set(template.variables)
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars
        
        if missing_vars:
            logger.warning(f"必要な変数が不足しています: {missing_vars}")
            return None
        
        try:
            # 変数置換
            prompt = template.template_content
            for var_name, var_value in variables.items():
                prompt = prompt.replace(f"{{{var_name}}}", var_value)
            
            # 使用回数をインクリメント
            template.usage_count += 1
            
            return prompt
        except Exception as e:
            logger.error(f"プロンプト生成エラー: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """テンプレート統計情報を取得"""
        templates = list(self.templates.values())
        
        stats = {
            'total_templates': len(templates),
            'default_templates': len([t for t in templates if not t.is_custom]),
            'custom_templates': len([t for t in templates if t.is_custom]),
            'by_category': {},
            'most_used': None,
            'recently_updated': []
        }
        
        # カテゴリ別集計
        category_counts = {}
        for template in templates:
            category_counts[template.category] = category_counts.get(template.category, 0) + 1
        stats['by_category'] = category_counts
        
        # 最も使用されたテンプレート
        if templates:
            most_used = max(templates, key=lambda t: t.usage_count)
            stats['most_used'] = {
                'id': most_used.id,
                'name': most_used.name,
                'usage_count': most_used.usage_count
            }
        
        # 最近更新されたテンプレート（最新5件）
        sorted_by_update = sorted(templates, key=lambda t: t.updated_at, reverse=True)
        stats['recently_updated'] = [
            {
                'id': t.id,
                'name': t.name,
                'updated_at': t.updated_at
            }
            for t in sorted_by_update[:5]
        ]
        
        return stats