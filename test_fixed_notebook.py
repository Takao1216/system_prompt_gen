#!/usr/bin/env python3
"""
Test the fixed notebook to ensure all critical functions work.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_critical_imports():
    """Test all critical imports that the notebook relies on."""
    print("🧪 Testing critical imports...")
    
    successes = []
    failures = []
    
    tests = [
        # Core modules with correct names
        ("PromptHistory", "from src.prompt_history import PromptHistory"),
        ("BatchProcessor", "from src.batch_processor import BatchProcessor"),
        ("CodeInputHandler", "from src.code_input_handler import CodeInputHandler, CodeInput"),
        ("CodeAnalyzer", "from src.code_analyzer import CodeAnalyzer"),
        ("PromptGenerator", "from src.generator import PromptGenerator"),  # Correct name
        ("PromptEvaluator", "from src.evaluator import PromptEvaluator"),
        ("TemplateManager", "from src.templates.template_manager import TemplateManager"),
        ("PromptImprovementWorkflow", "from src.langgraph_workflows.prompt_workflow import PromptImprovementWorkflow"),
        
        # Standard libraries
        ("asyncio", "import asyncio"),
        ("pandas", "import pandas as pd"),
        ("numpy", "import numpy as np"),
        ("matplotlib", "import matplotlib.pyplot as plt"),
        ("json", "import json"),
        ("dataclasses", "from dataclasses import dataclass"),
    ]
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            successes.append(name)
            print(f"  ✅ {name}")
        except Exception as e:
            failures.append((name, str(e)))
            print(f"  ❌ {name}: {str(e)}")
    
    return successes, failures

def test_basic_instantiation():
    """Test basic instantiation of key classes."""
    print(f"\n🏗️  Testing basic class instantiation...")
    
    successes = []
    failures = []
    
    try:
        from src.prompt_history import PromptHistory
        history = PromptHistory()
        successes.append("PromptHistory")
        print(f"  ✅ PromptHistory")
    except Exception as e:
        failures.append(("PromptHistory", str(e)))
        print(f"  ❌ PromptHistory: {str(e)}")
    
    try:
        from src.code_input_handler import CodeInputHandler
        handler = CodeInputHandler()
        successes.append("CodeInputHandler")
        print(f"  ✅ CodeInputHandler")
    except Exception as e:
        failures.append(("CodeInputHandler", str(e)))
        print(f"  ❌ CodeInputHandler: {str(e)}")
    
    try:
        from src.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        successes.append("CodeAnalyzer")
        print(f"  ✅ CodeAnalyzer")
    except Exception as e:
        failures.append(("CodeAnalyzer", str(e)))
        print(f"  ❌ CodeAnalyzer: {str(e)}")
    
    try:
        from src.generator import PromptGenerator
        generator = PromptGenerator()
        successes.append("PromptGenerator")
        print(f"  ✅ PromptGenerator")
    except Exception as e:
        failures.append(("PromptGenerator", str(e)))
        print(f"  ❌ PromptGenerator: {str(e)}")
    
    return successes, failures

def test_functionality():
    """Test basic functionality of key components."""
    print(f"\n⚙️  Testing basic functionality...")
    
    successes = []
    failures = []
    
    # Test PromptHistory functionality
    try:
        from src.prompt_history import PromptHistory
        history = PromptHistory()
        
        # Test save functionality with correct signature
        test_id = history.save_prompt(
            prompt_type="test",
            user_requirements="Test requirements",
            generated_prompt="Test prompt content"
        )
        
        # Test search functionality
        results = history.search_prompts("test")
        
        successes.append("PromptHistory functionality")
        print(f"  ✅ PromptHistory save/search")
    except Exception as e:
        failures.append(("PromptHistory functionality", str(e)))
        print(f"  ❌ PromptHistory functionality: {str(e)}")
    
    # Test CodeAnalyzer functionality
    try:
        from src.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        
        # Test basic analysis with correct method name
        sample_code = "def test(): return 'hello'"
        metrics = analyzer.analyze_python_ast(sample_code)
        
        successes.append("CodeAnalyzer functionality")
        print(f"  ✅ CodeAnalyzer analysis")
    except Exception as e:
        failures.append(("CodeAnalyzer functionality", str(e)))
        print(f"  ❌ CodeAnalyzer functionality: {str(e)}")
    
    return successes, failures

def test_async_compatibility():
    """Test async functionality."""
    print(f"\n🔄 Testing async compatibility...")
    
    import asyncio
    
    async def test_async_function():
        """Test basic async functionality."""
        await asyncio.sleep(0.001)
        return "async test passed"
    
    try:
        result = asyncio.run(test_async_function())
        print(f"  ✅ Basic async functionality")
        return True
    except Exception as e:
        print(f"  ❌ Async functionality: {str(e)}")
        return False

def generate_test_report(import_results, instantiation_results, functionality_results, async_result):
    """Generate a comprehensive test report."""
    
    import_successes, import_failures = import_results
    inst_successes, inst_failures = instantiation_results
    func_successes, func_failures = functionality_results
    
    total_tests = len(import_successes) + len(import_failures)
    successful_imports = len(import_successes)
    
    total_inst_tests = len(inst_successes) + len(inst_failures)
    successful_inst = len(inst_successes)
    
    total_func_tests = len(func_successes) + len(func_failures)
    successful_func = len(func_successes)
    
    report = f"""
📊 COMPREHENSIVE NOTEBOOK TESTING REPORT
==========================================

🔍 Import Testing:
  Total imports tested: {total_tests}
  Successful imports: {successful_imports}
  Failed imports: {len(import_failures)}
  Success rate: {(successful_imports/total_tests*100):.1f}%

🏗️  Instantiation Testing:
  Total classes tested: {total_inst_tests}
  Successfully instantiated: {successful_inst}
  Failed instantiations: {len(inst_failures)}
  Success rate: {(successful_inst/total_inst_tests*100):.1f}% if {total_inst_tests > 0} else 'N/A'

⚙️  Functionality Testing:
  Total functions tested: {total_func_tests}
  Working functions: {successful_func}
  Failed functions: {len(func_failures)}
  Success rate: {(successful_func/total_func_tests*100):.1f}% if {total_func_tests > 0} else 'N/A'

🔄 Async Compatibility: {'✅ Passed' if async_result else '❌ Failed'}

"""
    
    if import_failures:
        report += "❌ Failed Imports:\n"
        for name, error in import_failures:
            report += f"  - {name}: {error}\n"
        report += "\n"
    
    if inst_failures:
        report += "❌ Failed Instantiations:\n"
        for name, error in inst_failures:
            report += f"  - {name}: {error}\n"
        report += "\n"
    
    if func_failures:
        report += "❌ Failed Functions:\n"
        for name, error in func_failures:
            report += f"  - {name}: {error}\n"
        report += "\n"
    
    overall_success = (
        len(import_failures) == 0 and 
        len(inst_failures) == 0 and 
        len(func_failures) == 0 and
        async_result
    )
    
    if overall_success:
        report += "🎉 OVERALL RESULT: ALL TESTS PASSED! ✅\n"
        report += "   The fixed notebook should work correctly.\n"
    else:
        report += "⚠️  OVERALL RESULT: Some issues remain.\n"
        report += "   Review the failures above for manual fixes.\n"
    
    return report, overall_success

def main():
    """Run comprehensive testing."""
    
    print("🧪 COMPREHENSIVE TESTING OF FIXED NOTEBOOK")
    print("=" * 50)
    
    # Run all tests
    import_results = test_critical_imports()
    instantiation_results = test_basic_instantiation()
    functionality_results = test_functionality()
    async_result = test_async_compatibility()
    
    # Generate report
    report, overall_success = generate_test_report(
        import_results, 
        instantiation_results, 
        functionality_results, 
        async_result
    )
    
    print(report)
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())