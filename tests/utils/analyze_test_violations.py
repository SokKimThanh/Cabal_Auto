"""
Test Violations Analyzer
Scans all test files and reports violations of pytest template standards.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

@dataclass
class Violation:
    """Represents a test violation."""
    file: str
    line: int
    type: str
    message: str
    suggestion: str

class TestAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze test files."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.violations: List[Violation] = []
        self.has_pytest_import = False
        self.has_markers = False
        self.has_gui_imports = False
        self.has_windows_api = False
        self.has_platform_check = False
        self.has_display_check = False
        self.test_functions: List[str] = []
        self.function_returns: Dict[str, List[int]] = {}
        self.function_asserts: Dict[str, List[int]] = {}
        self.has_input_print = False
        self.module_level_gui_imports = []
        
    def visit_Import(self, node):
        """Check imports."""
        for alias in node.names:
            name = alias.name
            
            # Check for pytest import
            if name == 'pytest':
                self.has_pytest_import = True
            
            # Check for GUI imports at module level
            if name in ('tkinter', 'pyautogui', 'PIL', 'wx', 'PyQt5', 'PyQt6'):
                self.has_gui_imports = True
                self.module_level_gui_imports.append((node.lineno, name))
            
            # Check for Windows API
            if name in ('ctypes', 'win32api', 'win32con', 'win32gui'):
                self.has_windows_api = True
                
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Check from imports."""
        if node.module:
            # Check for pytest markers
            if node.module == 'pytest' or 'pytest' in node.module:
                self.has_pytest_import = True
            
            # Check for GUI imports
            if node.module in ('tkinter', 'pyautogui', 'PIL', 'wx', 'PyQt5', 'PyQt6'):
                self.has_gui_imports = True
                self.module_level_gui_imports.append((node.lineno, node.module))
            
            # Check for Windows-specific imports
            if 'ctypes.wintypes' in node.module or 'win32' in node.module:
                self.has_windows_api = True
                
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Analyze test functions."""
        func_name = node.name
        
        # Check if it's a test function
        if func_name.startswith('test_'):
            self.test_functions.append(func_name)
            
            # Check for markers
            if node.decorator_list:
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if isinstance(decorator.value, ast.Attribute):
                            if decorator.value.attr == 'mark':
                                self.has_markers = True
                    elif isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if hasattr(decorator.func.value, 'attr') and decorator.func.value.attr == 'mark':
                                self.has_markers = True
            
            # Analyze function body
            self.function_returns[func_name] = []
            self.function_asserts[func_name] = []
            
            for stmt in ast.walk(node):
                # Check for return statements
                if isinstance(stmt, ast.Return) and stmt.value is not None:
                    self.function_returns[func_name].append(stmt.lineno)
                
                # Check for assert statements
                if isinstance(stmt, ast.Assert):
                    self.function_asserts[func_name].append(stmt.lineno)
                
                # Check for input() or print() calls
                if isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Name):
                        if stmt.func.id in ('input', 'print'):
                            self.has_input_print = True
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Check for platform checks."""
        if isinstance(node.func, ast.Attribute):
            # Check for pytest.skip
            if node.func.attr == 'skip':
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pytest':
                    # Check if it's module-level skip
                    for keyword in node.keywords:
                        if keyword.arg == 'allow_module_level' and isinstance(keyword.value, ast.Constant):
                            if keyword.value.value is True:
                                self.has_platform_check = True
        
        self.generic_visit(node)
    
    def analyze(self):
        """Run analysis and generate violations."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(self.filepath))
            
            self.visit(tree)
            
            # Generate violations
            self._check_pytest_import()
            self._check_markers()
            self._check_assertions()
            self._check_returns()
            self._check_gui_imports()
            self._check_windows_api()
            
            return self.violations
            
        except SyntaxError as e:
            self.violations.append(Violation(
                file=str(self.filepath),
                line=e.lineno or 0,
                type="SYNTAX_ERROR",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax errors before running tests"
            ))
            return self.violations
    
    def _check_pytest_import(self):
        """Check if pytest is imported."""
        if self.test_functions and not self.has_pytest_import:
            self.violations.append(Violation(
                file=str(self.filepath),
                line=1,
                type="MISSING_PYTEST_IMPORT",
                message="Test file has test functions but doesn't import pytest",
                suggestion="Add: import pytest"
            ))
    
    def _check_markers(self):
        """Check for appropriate markers."""
        if not self.test_functions:
            return
        
        # Check for GUI imports without markers
        if self.has_gui_imports and not self.has_markers:
            self.violations.append(Violation(
                file=str(self.filepath),
                line=1,
                type="MISSING_GUI_MARKER",
                message="File has GUI imports but no @pytest.mark.gui marker",
                suggestion="Add: pytestmark = pytest.mark.gui (module-level) or @pytest.mark.gui on test functions"
            ))
        
        # Check for Windows API without markers
        if self.has_windows_api and not self.has_markers:
            self.violations.append(Violation(
                file=str(self.filepath),
                line=1,
                type="MISSING_WINDOWS_MARKER",
                message="File has Windows API imports but no @pytest.mark.windows marker",
                suggestion="Add: pytestmark = pytest.mark.windows"
            ))
    
    def _check_assertions(self):
        """Check for missing assertions in test functions."""
        for func_name in self.test_functions:
            has_asserts = len(self.function_asserts.get(func_name, [])) > 0
            has_returns = len(self.function_returns.get(func_name, [])) > 0
            
            if not has_asserts and not has_returns:
                self.violations.append(Violation(
                    file=str(self.filepath),
                    line=0,
                    type="NO_ASSERTIONS",
                    message=f"Test function '{func_name}' has no assertions",
                    suggestion=f"Add assert statements to verify test conditions in {func_name}"
                ))
    
    def _check_returns(self):
        """Check for test functions returning values."""
        for func_name, return_lines in self.function_returns.items():
            if return_lines:
                self.violations.append(Violation(
                    file=str(self.filepath),
                    line=return_lines[0],
                    type="TEST_RETURNS_VALUE",
                    message=f"Test function '{func_name}' returns a value (should use assert instead)",
                    suggestion=f"Replace 'return True/False' with assert statements in {func_name}"
                ))
    
    def _check_gui_imports(self):
        """Check for GUI imports without proper handling."""
        if self.module_level_gui_imports and not self.has_platform_check:
            for lineno, module in self.module_level_gui_imports:
                self.violations.append(Violation(
                    file=str(self.filepath),
                    line=lineno,
                    type="UNPROTECTED_GUI_IMPORT",
                    message=f"Module-level GUI import '{module}' without platform skip",
                    suggestion="Add module-level skip: if sys.platform != 'win32': pytest.skip(..., allow_module_level=True)"
                ))
    
    def _check_windows_api(self):
        """Check for Windows API usage without platform check."""
        if self.has_windows_api and not self.has_platform_check:
            self.violations.append(Violation(
                file=str(self.filepath),
                line=1,
                type="UNPROTECTED_WINDOWS_API",
                message="Windows API imports without platform check",
                suggestion="Add: if sys.platform != 'win32': pytest.skip('Requires Windows', allow_module_level=True)"
            ))


def analyze_test_directory(test_dir: Path) -> Dict[str, List[Violation]]:
    """Analyze all test files in directory."""
    results = {}
    
    for test_file in test_dir.rglob("test_*.py"):
        analyzer = TestAnalyzer(test_file)
        violations = analyzer.analyze()
        
        if violations:
            results[str(test_file.relative_to(test_dir.parent))] = violations
    
    return results


def print_report(results: Dict[str, List[Violation]]):
    """Print formatted violation report."""
    print("\n" + "="*80)
    print("TEST VIOLATIONS REPORT")
    print("="*80 + "\n")
    
    if not results:
        print("✅ No violations found! All tests follow the template.")
        return
    
    total_violations = sum(len(v) for v in results.values())
    print(f"Found {total_violations} violations in {len(results)} files\n")
    
    # Group by violation type
    by_type: Dict[str, List[tuple]] = {}
    for file, violations in results.items():
        for v in violations:
            if v.type not in by_type:
                by_type[v.type] = []
            by_type[v.type].append((file, v))
    
    # Print by type
    for vtype in sorted(by_type.keys()):
        items = by_type[vtype]
        print(f"\n{'='*80}")
        print(f"❌ {vtype} ({len(items)} occurrences)")
        print(f"{'='*80}")
        
        for file, v in items:
            print(f"\n📁 File: {file}")
            if v.line > 0:
                print(f"   Line: {v.line}")
            print(f"   Issue: {v.message}")
            print(f"   💡 Fix: {v.suggestion}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    for vtype, items in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {vtype:.<50} {len(items):>4}")
    print(f"{'='*80}")
    print(f"TOTAL: {total_violations} violations")
    print(f"{'='*80}\n")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests"
    
    print("Analyzing test files...")
    print(f"Test directory: {tests_dir}\n")
    
    results = analyze_test_directory(tests_dir)
    print_report(results)
    
    return 0 if not results else 1


if __name__ == "__main__":
    sys.exit(main())
