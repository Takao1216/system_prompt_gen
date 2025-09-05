#!/usr/bin/env python3
"""
Comprehensive validation report for notebook_v1.1.0-dev.ipynb
Identifies issues and suggests fixes for notebook cells.
"""

import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

@dataclass
class Issue:
    cell_number: int
    severity: str  # 'critical', 'warning', 'info'
    category: str
    description: str
    suggested_fix: str = ""

class NotebookValidator:
    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path
        self.issues: List[Issue] = []
        
    def load_notebook(self) -> Dict:
        """Load the notebook JSON."""
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_imports(self) -> List[Issue]:
        """Validate import statements in the notebook."""
        issues = []
        
        # Test actual imports
        import_tests = [
            # Incorrect imports that should be fixed
            {
                'incorrect': 'from src.generator import SystemPromptGenerator',
                'correct': 'from src.generator import PromptGenerator',
                'description': 'SystemPromptGenerator class does not exist, should be PromptGenerator'
            },
            {
                'incorrect': 'from src.langgraph_workflows.prompt_workflow import PromptWorkflow',
                'correct': 'from src.langgraph_workflows.prompt_workflow import PromptImprovementWorkflow',
                'description': 'PromptWorkflow class does not exist, should be PromptImprovementWorkflow'
            }
        ]
        
        for test in import_tests:
            try:
                exec(test['incorrect'])
            except ImportError:
                issues.append(Issue(
                    cell_number=0,  # Will be updated when scanning cells
                    severity='critical',
                    category='import_error',
                    description=test['description'],
                    suggested_fix=f"Change '{test['incorrect']}' to '{test['correct']}'"
                ))
        
        return issues
    
    def scan_notebook_cells(self) -> List[Issue]:
        """Scan notebook cells for issues."""
        notebook = self.load_notebook()
        issues = []
        
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                cell_content = ''.join(cell['source'])
                issues.extend(self.analyze_cell_content(i+1, cell_content))
        
        return issues
    
    def analyze_cell_content(self, cell_number: int, content: str) -> List[Issue]:
        """Analyze individual cell content for issues."""
        issues = []
        
        # Check for incorrect import statements
        if 'SystemPromptGenerator' in content:
            issues.append(Issue(
                cell_number=cell_number,
                severity='critical',
                category='import_error',
                description='SystemPromptGenerator class does not exist',
                suggested_fix='Replace SystemPromptGenerator with PromptGenerator'
            ))
        
        if 'PromptWorkflow' in content and 'PromptImprovementWorkflow' not in content:
            issues.append(Issue(
                cell_number=cell_number,
                severity='critical', 
                category='import_error',
                description='PromptWorkflow class does not exist',
                suggested_fix='Replace PromptWorkflow with PromptImprovementWorkflow'
            ))
        
        # Check for API key usage without proper error handling
        if 'ANTHROPIC_API_KEY' in content and 'getenv' in content:
            if 'if not' not in content and 'try:' not in content:
                issues.append(Issue(
                    cell_number=cell_number,
                    severity='warning',
                    category='api_error_handling',
                    description='API key usage without proper error handling',
                    suggested_fix='Add error handling for missing API keys'
                ))
        
        # Check for display/widget usage
        if any(widget in content for widget in ['ipywidgets', 'display(', 'HTML(']):
            issues.append(Issue(
                cell_number=cell_number,
                severity='info',
                category='interactive_widget',
                description='Contains interactive widgets that may not work in all environments',
                suggested_fix='Add fallback for non-interactive environments'
            ))
        
        # Check for async code without proper handling
        if 'await ' in content and 'async def' not in content:
            if 'asyncio.run(' not in content and 'await asyncio.gather(' not in content:
                issues.append(Issue(
                    cell_number=cell_number,
                    severity='warning',
                    category='async_handling',
                    description='Async code may need proper execution context',
                    suggested_fix='Ensure async code is properly wrapped for notebook execution'
                ))
        
        return issues
    
    def test_module_availability(self) -> List[Issue]:
        """Test if all required modules are available."""
        issues = []
        
        # Test core modules
        modules_to_test = [
            ('src.prompt_history', 'PromptHistory'),
            ('src.batch_processor', 'BatchProcessor'),
            ('src.code_input_handler', ['CodeInputHandler', 'CodeInput']),
            ('src.code_analyzer', 'CodeAnalyzer'),
            ('src.generator', 'PromptGenerator'),  # Correct class name
            ('src.evaluator', 'PromptEvaluator'),
            ('src.templates.template_manager', 'TemplateManager'),
            ('src.langgraph_workflows.prompt_workflow', 'PromptImprovementWorkflow'),  # Correct class
        ]
        
        for module, classes in modules_to_test:
            try:
                mod = __import__(module, fromlist=classes if isinstance(classes, list) else [classes])
                
                if isinstance(classes, list):
                    for cls in classes:
                        if not hasattr(mod, cls):
                            issues.append(Issue(
                                cell_number=0,
                                severity='critical',
                                category='missing_class',
                                description=f'Class {cls} not found in module {module}',
                                suggested_fix=f'Check if class {cls} is properly defined and exported'
                            ))
                else:
                    if not hasattr(mod, classes):
                        issues.append(Issue(
                            cell_number=0,
                            severity='critical',
                            category='missing_class', 
                            description=f'Class {classes} not found in module {module}',
                            suggested_fix=f'Check if class {classes} is properly defined and exported'
                        ))
                        
            except ImportError as e:
                issues.append(Issue(
                    cell_number=0,
                    severity='critical',
                    category='missing_module',
                    description=f'Module {module} cannot be imported: {str(e)}',
                    suggested_fix=f'Ensure module {module} exists and is properly implemented'
                ))
        
        return issues
    
    def validate_dependencies(self) -> List[Issue]:
        """Check if all required dependencies are available."""
        issues = []
        
        required_deps = [
            'pandas', 'numpy', 'matplotlib', 'anthropic', 'langgraph',
            'ipywidgets', 'asyncio'
        ]
        
        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError:
                issues.append(Issue(
                    cell_number=0,
                    severity='warning' if dep in ['ipywidgets'] else 'critical',
                    category='missing_dependency',
                    description=f'Required dependency {dep} is not available',
                    suggested_fix=f'Install {dep} using pip install {dep}'
                ))
        
        return issues
    
    def generate_fixes(self) -> Dict[str, str]:
        """Generate specific code fixes for identified issues."""
        fixes = {}
        
        # Import fixes
        fixes['import_fixes'] = """
# Correct import statements:
from src.generator import PromptGenerator  # Not SystemPromptGenerator
from src.langgraph_workflows.prompt_workflow import PromptImprovementWorkflow  # Not PromptWorkflow

# Safe API key handling:
import os
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("Warning: ANTHROPIC_API_KEY not set. Some features may not work.")
    # Use mock or skip API-dependent functionality
"""
        
        # Widget fallback
        fixes['widget_fallback'] = """
# Fallback for interactive widgets in non-notebook environments:
try:
    from IPython.display import display, HTML
    import ipywidgets as widgets
    INTERACTIVE_MODE = True
except ImportError:
    # Mock implementations for testing
    def display(*args, **kwargs):
        for arg in args:
            print(f"[DISPLAY] {arg}")
    
    def HTML(content):
        return f"[HTML] {content}"
    
    INTERACTIVE_MODE = False
"""
        
        # Async handling
        fixes['async_handling'] = """
# Proper async handling in notebooks:
import asyncio

# For async functions in notebook cells:
async def run_async_demo():
    # Your async code here
    pass

# Run with:
await run_async_demo()  # In notebook
# or
# asyncio.run(run_async_demo())  # In regular Python
"""
        
        return fixes
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete validation and return results."""
        print("🔍 Running comprehensive notebook validation...")
        
        all_issues = []
        all_issues.extend(self.validate_dependencies())
        all_issues.extend(self.test_module_availability())
        all_issues.extend(self.scan_notebook_cells())
        
        # Categorize issues
        critical_issues = [i for i in all_issues if i.severity == 'critical']
        warning_issues = [i for i in all_issues if i.severity == 'warning']
        info_issues = [i for i in all_issues if i.severity == 'info']
        
        results = {
            'total_issues': len(all_issues),
            'critical_issues': len(critical_issues),
            'warning_issues': len(warning_issues),
            'info_issues': len(info_issues),
            'issues_by_severity': {
                'critical': critical_issues,
                'warning': warning_issues,
                'info': info_issues
            },
            'suggested_fixes': self.generate_fixes()
        }
        
        return results

def main():
    """Run validation and generate report."""
    notebook_path = "notebooks/current/notebook_v1.1.0-dev.ipynb"
    
    if not Path(notebook_path).exists():
        print(f"❌ Error: Notebook not found at {notebook_path}")
        return 1
    
    validator = NotebookValidator(notebook_path)
    results = validator.run_validation()
    
    print("\n" + "=" * 60)
    print("📊 NOTEBOOK VALIDATION REPORT")
    print("=" * 60)
    
    print(f"\n📈 Summary:")
    print(f"  Total issues found: {results['total_issues']}")
    print(f"  🔴 Critical: {results['critical_issues']}")
    print(f"  🟡 Warning: {results['warning_issues']}")
    print(f"  🔵 Info: {results['info_issues']}")
    
    # Report critical issues
    if results['critical_issues'] > 0:
        print(f"\n🔴 Critical Issues (Must Fix):")
        for issue in results['issues_by_severity']['critical']:
            if issue.cell_number > 0:
                print(f"  Cell {issue.cell_number}: {issue.description}")
            else:
                print(f"  Global: {issue.description}")
            if issue.suggested_fix:
                print(f"    Fix: {issue.suggested_fix}")
    
    # Report warnings
    if results['warning_issues'] > 0:
        print(f"\n🟡 Warnings (Should Fix):")
        for issue in results['issues_by_severity']['warning']:
            if issue.cell_number > 0:
                print(f"  Cell {issue.cell_number}: {issue.description}")
            else:
                print(f"  Global: {issue.description}")
            if issue.suggested_fix:
                print(f"    Fix: {issue.suggested_fix}")
    
    # Show fixes
    print(f"\n🔧 Suggested Code Fixes:")
    for fix_name, fix_code in results['suggested_fixes'].items():
        print(f"\n{fix_name.replace('_', ' ').title()}:")
        print(fix_code)
    
    print("\n" + "=" * 60)
    
    if results['critical_issues'] == 0:
        print("✅ No critical issues found! Notebook should work correctly.")
        return 0
    else:
        print(f"❌ Found {results['critical_issues']} critical issues that must be fixed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())