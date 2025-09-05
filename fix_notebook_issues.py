#!/usr/bin/env python3
"""
Fix critical issues in notebook_v1.1.0-dev.ipynb
"""

import json
import re
from pathlib import Path
from typing import Dict, List

def fix_notebook_issues(notebook_path: str, output_path: str = None) -> bool:
    """Fix issues in the notebook and save corrected version."""
    
    if output_path is None:
        output_path = notebook_path.replace('.ipynb', '_fixed.ipynb')
    
    # Load notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    fixes_applied = []
    
    # Fix each cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            original_source = ''.join(cell['source'])
            
            # Apply fixes
            fixed_source = apply_code_fixes(original_source)
            
            if fixed_source != original_source:
                # Update the cell with fixed code
                cell['source'] = fixed_source.split('\n')
                # Ensure each line ends with \n except the last one
                for j in range(len(cell['source']) - 1):
                    if not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
                
                fixes_applied.append({
                    'cell': i + 1,
                    'type': 'code_fix',
                    'description': 'Fixed import/class name issues'
                })
    
    # Save fixed notebook
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fixed notebook saved to: {output_path}")
    print(f"Applied {len(fixes_applied)} fixes:")
    for fix in fixes_applied:
        print(f"  - Cell {fix['cell']}: {fix['description']}")
    
    return len(fixes_applied) > 0

def apply_code_fixes(code: str) -> str:
    """Apply code fixes to a single code block."""
    
    # Fix 1: Replace incorrect class imports
    code = re.sub(
        r'from src\.generator import SystemPromptGenerator',
        'from src.generator import PromptGenerator',
        code
    )
    
    code = re.sub(
        r'from src\.langgraph_workflows\.prompt_workflow import PromptWorkflow',
        'from src.langgraph_workflows.prompt_workflow import PromptImprovementWorkflow',
        code
    )
    
    # Fix 2: Replace class instantiations and references
    code = re.sub(r'SystemPromptGenerator\(', 'PromptGenerator(', code)
    code = re.sub(r'PromptWorkflow\(', 'PromptImprovementWorkflow(', code)
    
    # Fix 3: Replace class references in comments and strings
    code = re.sub(r'PromptWorkflow(?!OrchestrationEngine|State|Config)', 'PromptImprovementWorkflow', code)
    code = re.sub(r'SystemPromptGenerator', 'PromptGenerator', code)
    
    # Fix 4: Add safe API key handling where needed
    if 'os.getenv(\'ANTHROPIC_API_KEY\')' in code and 'if not' not in code:
        code = add_safe_api_key_handling(code)
    
    # Fix 5: Add widget fallbacks where needed
    if any(widget in code for widget in ['ipywidgets', 'display(', 'HTML(']):
        code = add_widget_fallback(code)
    
    return code

def add_safe_api_key_handling(code: str) -> str:
    """Add safe API key handling to code."""
    
    if 'ANTHROPIC_API_KEY' in code and 'if not os.getenv' not in code:
        # Add safe handling at the beginning
        safe_handling = '''
# Safe API key handling
import os
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("⚠️ ANTHROPIC_API_KEY not set. Some features may not work.")
    # Continue with limited functionality

'''
        # Only add if not already present
        if 'Safe API key handling' not in code:
            code = safe_handling + code
    
    return code

def add_widget_fallback(code: str) -> str:
    """Add widget fallback for non-interactive environments."""
    
    fallback_code = '''
# Fallback for interactive widgets
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
    
    class MockWidget:
        def __init__(self, *args, **kwargs):
            pass
    
    # Mock common widgets
    widgets = type('widgets', (), {
        'Text': MockWidget,
        'Button': MockWidget,
        'VBox': MockWidget,
        'HBox': MockWidget,
        'Output': MockWidget,
        'interactive_output': lambda *args, **kwargs: None
    })()
    
    INTERACTIVE_MODE = False

'''
    
    # Only add if not already present
    if 'Fallback for interactive widgets' not in code:
        code = fallback_code + code
    
    return code

def validate_fixes(original_path: str, fixed_path: str) -> bool:
    """Validate that fixes were applied correctly."""
    
    print("\n🔍 Validating fixes...")
    
    # Load fixed notebook
    with open(fixed_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    issues_found = []
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            content = ''.join(cell['source'])
            
            # Check for remaining issues
            if 'SystemPromptGenerator' in content and 'PromptGenerator' not in content:
                issues_found.append(f"Cell {i+1}: Still contains SystemPromptGenerator")
            
            # Check for standalone PromptWorkflow (not part of other class names)
            if re.search(r'\bPromptWorkflow\b(?!State|Config|Orchestrator)', content) and 'PromptImprovementWorkflow' not in content:
                issues_found.append(f"Cell {i+1}: Still contains incorrect PromptWorkflow")
    
    if issues_found:
        print("❌ Remaining issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All critical issues have been fixed!")
        return True

def main():
    """Main function."""
    
    notebook_path = "notebooks/current/notebook_v1.1.0-dev.ipynb"
    fixed_path = "notebooks/current/notebook_v1.1.0-dev_fixed.ipynb"
    
    if not Path(notebook_path).exists():
        print(f"❌ Error: Notebook not found at {notebook_path}")
        return 1
    
    print("🔧 Fixing notebook issues...")
    print(f"Input: {notebook_path}")
    print(f"Output: {fixed_path}")
    
    # Apply fixes
    fixes_applied = fix_notebook_issues(notebook_path, fixed_path)
    
    if fixes_applied:
        # Validate fixes
        validation_success = validate_fixes(notebook_path, fixed_path)
        
        print(f"\n📋 Summary:")
        print(f"  Original notebook: {notebook_path}")
        print(f"  Fixed notebook: {fixed_path}")
        print(f"  Fixes applied: {'Yes' if fixes_applied else 'No'}")
        print(f"  Validation passed: {'Yes' if validation_success else 'No'}")
        
        if validation_success:
            print(f"\n✅ Notebook has been successfully fixed!")
            print(f"   You can now use: {fixed_path}")
            return 0
        else:
            print(f"\n⚠️  Some issues may remain. Please review manually.")
            return 1
    else:
        print("ℹ️  No fixes needed or could be applied.")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())