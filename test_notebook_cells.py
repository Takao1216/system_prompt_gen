#!/usr/bin/env python3
"""
Systematic testing script for notebook_v1.1.0-dev.ipynb
Tests each code cell to ensure they work correctly.
"""

import asyncio
import json
import os
import sys
import traceback
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

@dataclass
class TestResult:
    cell_number: int
    cell_type: str
    success: bool
    error_message: str = ""
    execution_time: float = 0.0
    source_preview: str = ""

class NotebookTester:
    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path
        self.results: List[TestResult] = []
        self.execution_globals = {}
        
    def load_notebook(self) -> Dict:
        """Load the notebook JSON."""
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_code_from_cell(self, cell: Dict) -> str:
        """Extract code from a cell."""
        if cell['cell_type'] != 'code':
            return ""
        return ''.join(cell['source'])
    
    def get_cell_preview(self, cell: Dict, max_length: int = 80) -> str:
        """Get a preview of the cell content."""
        source = ''.join(cell['source']).strip()
        if len(source) <= max_length:
            return source
        return source[:max_length] + "..."
    
    def is_interactive_widget_code(self, code: str) -> bool:
        """Check if code contains interactive widgets that should be skipped in testing."""
        interactive_keywords = [
            'ipywidgets',
            'widgets.interact',
            'display(',
            'HTML(',
            'interactive_output'
        ]
        return any(keyword in code for keyword in interactive_keywords)
    
    def is_async_cell(self, code: str) -> bool:
        """Check if cell contains async code that needs special handling."""
        return 'await ' in code or code.strip().startswith('async def')
    
    def handle_missing_dependencies(self, code: str) -> str:
        """Add mock implementations for missing dependencies."""
        # Mock API keys if not available
        if 'os.getenv' in code and 'API_KEY' in code:
            mock_env = """
# Mock environment variables for testing
import os
if not os.getenv('OPENAI_API_KEY'):
    os.environ['OPENAI_API_KEY'] = 'test-key-for-testing'
if not os.getenv('ANTHROPIC_API_KEY'):
    os.environ['ANTHROPIC_API_KEY'] = 'test-key-for-testing'
"""
            code = mock_env + "\n" + code
        
        # Mock display functions for non-interactive environments
        if 'display(' in code:
            mock_display = """
# Mock display function for testing
def display(*args, **kwargs):
    for arg in args:
        print(f"[DISPLAY] {arg}")
"""
            code = mock_display + "\n" + code
            
        return code
    
    async def execute_code_cell(self, cell_number: int, code: str) -> TestResult:
        """Execute a single code cell and return test result."""
        import time
        
        source_preview = self.get_cell_preview({'source': [code], 'cell_type': 'code'})
        result = TestResult(
            cell_number=cell_number,
            cell_type='code',
            success=False,
            source_preview=source_preview
        )
        
        if not code.strip():
            result.success = True
            return result
        
        # Skip interactive widget code
        if self.is_interactive_widget_code(code):
            print(f"  Skipping interactive widget cell {cell_number}")
            result.success = True
            result.error_message = "Skipped - interactive widgets"
            return result
        
        try:
            start_time = time.time()
            
            # Handle missing dependencies
            code = self.handle_missing_dependencies(code)
            
            # Execute the code
            if self.is_async_cell(code):
                # Handle async code
                if 'async def' in code:
                    # Define async function
                    exec(code, self.execution_globals)
                else:
                    # Execute async code
                    await eval(f"async lambda: {code}", self.execution_globals)()
            else:
                exec(code, self.execution_globals)
            
            result.execution_time = time.time() - start_time
            result.success = True
            
        except ImportError as e:
            result.error_message = f"Import Error: {str(e)}"
            print(f"  Import error in cell {cell_number}: {str(e)}")
        except NameError as e:
            result.error_message = f"Name Error: {str(e)}"
            print(f"  Name error in cell {cell_number}: {str(e)}")
        except Exception as e:
            result.error_message = f"{type(e).__name__}: {str(e)}"
            print(f"  Error in cell {cell_number}: {type(e).__name__}: {str(e)}")
            if "--verbose" in sys.argv:
                print(f"    Traceback: {traceback.format_exc()}")
        
        return result
    
    async def test_imports(self) -> Dict[str, bool]:
        """Test critical module imports."""
        print("Testing critical imports...")
        
        imports_to_test = [
            "from src.prompt_history import PromptHistory",
            "from src.batch_processor import BatchProcessor", 
            "from src.code_input_handler import CodeInputHandler, CodeInput",
            "from src.code_analyzer import CodeAnalyzer",
            "from src.generator import SystemPromptGenerator",
            "from src.evaluator import PromptEvaluator"
        ]
        
        results = {}
        
        for import_stmt in imports_to_test:
            try:
                exec(import_stmt, self.execution_globals)
                results[import_stmt] = True
                print(f"  ✅ {import_stmt}")
            except Exception as e:
                results[import_stmt] = False
                print(f"  ❌ {import_stmt} - {str(e)}")
        
        return results
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run tests on all code cells in the notebook."""
        print("Loading notebook...")
        notebook = self.load_notebook()
        
        print(f"Found {len(notebook['cells'])} cells")
        
        # Test imports first
        import_results = await self.test_imports()
        
        print("\nTesting code cells...")
        
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                print(f"Testing cell {i+1}/{len(notebook['cells'])}...")
                code = self.extract_code_from_cell(cell)
                result = await self.execute_code_cell(i+1, code)
                self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_cells = len(self.results)
        successful_cells = sum(1 for r in self.results if r.success)
        failed_cells = total_cells - successful_cells
        
        report = f"""
NOTEBOOK TESTING REPORT
======================

Summary:
- Total code cells tested: {total_cells}
- Successful executions: {successful_cells}
- Failed executions: {failed_cells}
- Success rate: {(successful_cells/total_cells*100):.1f}%

"""
        
        if failed_cells > 0:
            report += "Failed Cells:\n"
            for result in self.results:
                if not result.success:
                    report += f"  Cell {result.cell_number}: {result.error_message}\n"
                    report += f"    Preview: {result.source_preview}\n\n"
        
        # Group errors by type
        error_types = {}
        for result in self.results:
            if not result.success and result.error_message:
                error_type = result.error_message.split(':')[0]
                if error_type not in error_types:
                    error_types[error_type] = 0
                error_types[error_type] += 1
        
        if error_types:
            report += "Error Types Summary:\n"
            for error_type, count in error_types.items():
                report += f"  {error_type}: {count} occurrences\n"
        
        return report

async def main():
    """Main testing function."""
    notebook_path = "notebooks/current/notebook_v1.1.0-dev.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"Error: Notebook not found at {notebook_path}")
        return 1
    
    print("🧪 Starting systematic notebook testing...")
    print(f"Notebook: {notebook_path}")
    print("=" * 50)
    
    tester = NotebookTester(notebook_path)
    
    try:
        results = await tester.run_all_tests()
        
        print("\n" + "=" * 50)
        print(tester.generate_report())
        
        # Return appropriate exit code
        failed_count = sum(1 for r in results if not r.success)
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        print(f"Critical error during testing: {e}")
        if "--verbose" in sys.argv:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)