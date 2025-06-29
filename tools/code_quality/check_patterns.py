#!/usr/bin/env python3
"""
RSMT Code Pattern Checker
Validates code against project-specific patterns and best practices.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import argparse


class RSMTPatternChecker:
    """Checks for RSMT-specific code patterns and anti-patterns."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
        # Prohibited patterns
        self.prohibited_imports = {
            'from torch import *': "Use explicit imports instead of star imports",
            'import torch as *': "Use explicit imports instead of star imports",
            'from numpy import *': "Use explicit imports instead of star imports",
            'import numpy as *': "Use explicit imports instead of star imports",
        }
        
        # Required patterns for specific file types
        self.required_patterns = {
            'model': ['class.*Model.*:', '__init__', 'forward'],
            'trainer': ['class.*Trainer.*:', '__init__', 'train'],
            'dataset': ['class.*Dataset.*:', '__len__', '__getitem__'],
        }
        
        # Deprecated function patterns
        self.deprecated_functions = {
            'torch.load': "Use rsmt.utils.checkpoint.load_checkpoint instead",
            'torch.save': "Use rsmt.utils.checkpoint.save_checkpoint instead",
            'np.random.seed': "Use rsmt.utils.random.set_seed instead",
            'random.seed': "Use rsmt.utils.random.set_seed instead",
        }
        
        # File naming conventions
        self.naming_patterns = {
            'test_': r'^test_[a-z][a-z0-9_]*\.py$',
            'model': r'^[a-z][a-z0-9_]*_model\.py$',
            'trainer': r'^[a-z][a-z0-9_]*_trainer\.py$',
            'dataset': r'^[a-z][a-z0-9_]*_dataset\.py$',
        }

    def check_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check a single Python file for pattern violations."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check file naming
            issues.extend(self._check_file_naming(file_path))
            
            # Check prohibited imports
            issues.extend(self._check_prohibited_imports(file_path, content))
            
            # Check deprecated functions
            issues.extend(self._check_deprecated_functions(file_path, content))
            
            # Check required patterns
            issues.extend(self._check_required_patterns(file_path, content))
            
            # Parse AST for deeper checks
            try:
                tree = ast.parse(content)
                issues.extend(self._check_ast_patterns(file_path, tree))
            except SyntaxError as e:
                issues.append({
                    'file': str(file_path),
                    'line': e.lineno or 0,
                    'type': 'error',
                    'message': f"Syntax error: {e.msg}"
                })
            
        except Exception as e:
            issues.append({
                'file': str(file_path),
                'line': 0,
                'type': 'error',
                'message': f"Failed to check file: {e}"
            })
        
        return issues

    def _check_file_naming(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check file naming conventions."""
        issues = []
        filename = file_path.name
        
        # Skip __init__.py and __main__.py
        if filename.startswith('__') and filename.endswith('__.py'):
            return issues
        
        # Check specific naming patterns
        for pattern_type, regex in self.naming_patterns.items():
            if pattern_type in filename and not re.match(regex, filename):
                issues.append({
                    'file': str(file_path),
                    'line': 0,
                    'type': 'warning',
                    'message': f"File naming: {filename} should match pattern {regex}"
                })
        
        return issues

    def _check_prohibited_imports(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check for prohibited import patterns."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            for pattern, message in self.prohibited_imports.items():
                if pattern in line:
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'error',
                        'message': f"Prohibited import: {message}"
                    })
        
        return issues

    def _check_deprecated_functions(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check for deprecated function usage."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for func, message in self.deprecated_functions.items():
                if func in line and not line.strip().startswith('#'):
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'warning',
                        'message': f"Deprecated function: {message}"
                    })
        
        return issues

    def _check_required_patterns(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Check for required patterns in specific file types."""
        issues = []
        filename = file_path.name.lower()
        
        for file_type, patterns in self.required_patterns.items():
            if file_type in filename:
                for pattern in patterns:
                    if not re.search(pattern, content):
                        issues.append({
                            'file': str(file_path),
                            'line': 0,
                            'type': 'warning',
                            'message': f"Missing required pattern for {file_type}: {pattern}"
                        })
        
        return issues

    def _check_ast_patterns(self, file_path: Path, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check AST for code patterns."""
        issues = []
        
        class PatternVisitor(ast.NodeVisitor):
            def __init__(self, checker, file_path):
                self.checker = checker
                self.file_path = file_path
                self.issues = []
            
            def visit_FunctionDef(self, node):
                # Check for missing docstrings in public functions
                if (not node.name.startswith('_') and 
                    not ast.get_docstring(node) and 
                    'rsmt/' in str(self.file_path)):
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'type': 'warning',
                        'message': f"Public function '{node.name}' missing docstring"
                    })
                
                # Check for overly complex functions
                if self._count_nodes(node) > 50:
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'type': 'warning',
                        'message': f"Function '{node.name}' is too complex (>50 nodes)"
                    })
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check for missing docstrings in public classes
                if (not node.name.startswith('_') and 
                    not ast.get_docstring(node) and 
                    'rsmt/' in str(self.file_path)):
                    self.issues.append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'type': 'warning',
                        'message': f"Public class '{node.name}' missing docstring"
                    })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for unused imports (basic check)
                for alias in node.names:
                    if alias.name in ['os', 'sys'] and 'test' not in str(self.file_path):
                        # This is a simplified check - would need more sophisticated analysis
                        pass
                
                self.generic_visit(node)
            
            def _count_nodes(self, node):
                """Count AST nodes in a function."""
                count = 1
                for child in ast.walk(node):
                    count += 1
                return count
        
        visitor = PatternVisitor(self, file_path)
        visitor.visit(tree)
        issues.extend(visitor.issues)
        
        return issues


def main():
    parser = argparse.ArgumentParser(description='Check RSMT code patterns')
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues where possible')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    checker = RSMTPatternChecker()
    all_issues = []
    
    # Get files to check
    if args.files:
        files = [Path(f) for f in args.files if f.endswith('.py')]
    else:
        # Check all Python files in rsmt/, scripts/, tests/
        files = []
        for pattern in ['rsmt/**/*.py', 'scripts/**/*.py', 'tests/**/*.py']:
            files.extend(Path('.').glob(pattern))
    
    # Check each file
    for file_path in files:
        if file_path.exists():
            issues = checker.check_file(file_path)
            all_issues.extend(issues)
    
    # Report issues
    errors = [i for i in all_issues if i['type'] == 'error']
    warnings = [i for i in all_issues if i['type'] == 'warning']
    
    if args.verbose or errors or warnings:
        print(f"RSMT Code Pattern Check Results:")
        print(f"Files checked: {len(files)}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print()
    
    # Print errors
    for issue in errors:
        print(f"ERROR: {issue['file']}:{issue['line']} - {issue['message']}")
    
    # Print warnings
    for issue in warnings:
        print(f"WARNING: {issue['file']}:{issue['line']} - {issue['message']}")
    
    # Exit code
    if errors:
        sys.exit(1)
    elif warnings and not args.verbose:
        print(f"\n{len(warnings)} warnings found. Use --verbose for details.")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
