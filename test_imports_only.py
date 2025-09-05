#!/usr/bin/env python3
"""
Quick import and basic functionality testing for the notebook modules.
"""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test all critical imports from the notebook."""
    print("Testing critical module imports...")
    
    tests = [
        # Core modules
        ("prompt_history", "from src.prompt_history import PromptHistory"),
        ("batch_processor", "from src.batch_processor import BatchProcessor"), 
        ("code_input_handler", "from src.code_input_handler import CodeInputHandler, CodeInput"),
        ("code_analyzer", "from src.code_analyzer import CodeAnalyzer"),
        ("generator", "from src.generator import SystemPromptGenerator"),
        ("evaluator", "from src.evaluator import PromptEvaluator"),
        
        # Template modules
        ("template_manager", "from src.templates.template_manager import TemplateManager"),
        
        # LangGraph workflows  
        ("prompt_workflow", "from src.langgraph_workflows.prompt_workflow import PromptWorkflow"),
        
        # Standard libraries used in notebook
        ("asyncio", "import asyncio"),
        ("json", "import json"),
        ("pandas", "import pandas as pd"),
        ("numpy", "import numpy as np"),
        ("matplotlib", "import matplotlib.pyplot as plt"),
        ("dataclasses", "from dataclasses import dataclass"),
    ]
    
    results = {}
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            results[name] = True
            print(f"  ✅ {name}: {import_stmt}")
        except ImportError as e:
            results[name] = False
            print(f"  ❌ {name}: Import Error - {str(e)}")
        except Exception as e:
            results[name] = False
            print(f"  ⚠️  {name}: {type(e).__name__} - {str(e)}")
    
    return results

def test_basic_functionality():
    """Test basic functionality of imported modules."""
    print("\nTesting basic functionality...")
    
    try:
        # Test PromptHistory
        from src.prompt_history import PromptHistory
        history = PromptHistory()
        print("  ✅ PromptHistory instantiation works")
    except Exception as e:
        print(f"  ❌ PromptHistory instantiation failed: {e}")
    
    try:
        # Test CodeInputHandler
        from src.code_input_handler import CodeInputHandler, CodeInput
        handler = CodeInputHandler()
        print("  ✅ CodeInputHandler instantiation works")
    except Exception as e:
        print(f"  ❌ CodeInputHandler instantiation failed: {e}")
    
    try:
        # Test CodeAnalyzer
        from src.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        print("  ✅ CodeAnalyzer instantiation works")
    except Exception as e:
        print(f"  ❌ CodeAnalyzer instantiation failed: {e}")
    
    try:
        # Test SystemPromptGenerator (without API keys)
        from src.generator import SystemPromptGenerator
        generator = SystemPromptGenerator()
        print("  ✅ SystemPromptGenerator instantiation works")
    except Exception as e:
        print(f"  ❌ SystemPromptGenerator instantiation failed: {e}")

def check_file_structure():
    """Check if all expected files exist."""
    print("\nChecking file structure...")
    
    expected_files = [
        "src/__init__.py",
        "src/prompt_history.py",
        "src/batch_processor.py", 
        "src/code_input_handler.py",
        "src/code_analyzer.py",
        "src/generator.py",
        "src/evaluator.py",
        "src/templates/__init__.py",
        "src/templates/template_manager.py",
        "src/langgraph_workflows/__init__.py",
        "src/langgraph_workflows/prompt_workflow.py",
    ]
    
    for file_path in expected_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")

def test_notebook_compatibility():
    """Test notebook-specific compatibility."""
    print("\nTesting notebook compatibility...")
    
    try:
        # Test IPython/Jupyter related imports that might be in the notebook
        import IPython
        print("  ✅ IPython available")
    except ImportError:
        print("  ⚠️  IPython not available (normal in non-notebook environments)")
    
    try:
        # Test async functionality
        import asyncio
        
        async def test_async():
            await asyncio.sleep(0.001)
            return "async works"
        
        result = asyncio.run(test_async())
        print("  ✅ Asyncio functionality works")
    except Exception as e:
        print(f"  ❌ Asyncio functionality failed: {e}")

def main():
    """Run all tests."""
    print("🧪 Notebook Import and Functionality Testing")
    print("=" * 50)
    
    check_file_structure()
    import_results = test_imports()
    test_basic_functionality()
    test_notebook_compatibility()
    
    # Summary
    total_imports = len(import_results)
    successful_imports = sum(1 for success in import_results.values() if success)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print(f"Import success rate: {successful_imports}/{total_imports} ({successful_imports/total_imports*100:.1f}%)")
    
    if successful_imports < total_imports:
        print("\nFailed imports:")
        for name, success in import_results.items():
            if not success:
                print(f"  - {name}")
        return 1
    else:
        print("All critical imports successful! ✅")
        return 0

if __name__ == "__main__":
    sys.exit(main())