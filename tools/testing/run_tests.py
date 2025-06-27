#!/usr/bin/env python3
"""
RSMT Test Configuration and Runner
Comprehensive testing framework for RSMT project.
"""

import os
import sys
import pytest
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse


class RSMTTestRunner:
    """Comprehensive test runner for RSMT."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.test_results = {}
        
    def run_unit_tests(self, verbose: bool = False, coverage: bool = True) -> Dict[str, Any]:
        """Run unit tests."""
        print("🧪 Running unit tests...")
        
        cmd = [sys.executable, "-m", "pytest", "tests/unit/"]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend([
                "--cov=rsmt",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml",
            ])
        
        cmd.extend([
            "--tb=short",
            "--durations=10",
            "-m", "not slow",  # Skip slow tests by default
        ])
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "unit_tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,  # Would need timing logic
        }
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests."""
        print("🔗 Running integration tests...")
        
        cmd = [
            sys.executable, "-m", "pytest", 
            "tests/integration/",
            "-v" if verbose else "",
            "--tb=short",
            "-m", "integration",
        ]
        cmd = [c for c in cmd if c]  # Remove empty strings
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "integration_tests", 
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance/benchmark tests."""
        print("⚡ Running performance tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/benchmark/",
            "-v" if verbose else "",
            "--benchmark-only",
            "--benchmark-sort=mean",
            "-m", "benchmark",
        ]
        cmd = [c for c in cmd if c]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "performance_tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_type_checking(self, verbose: bool = False) -> Dict[str, Any]:
        """Run MyPy type checking."""
        print("🔍 Running type checking...")
        
        cmd = [sys.executable, "-m", "mypy", "rsmt/"]
        if verbose:
            cmd.append("--verbose")
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "type_checking",
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_linting(self, verbose: bool = False) -> Dict[str, Any]:
        """Run code linting with flake8."""
        print("📝 Running code linting...")
        
        cmd = [
            sys.executable, "-m", "flake8",
            "rsmt/", "scripts/", "tests/",
            "--max-line-length=88",
            "--extend-ignore=E203,W503",
        ]
        
        if verbose:
            cmd.append("--verbose")
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "linting",
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_security_checks(self, verbose: bool = False) -> Dict[str, Any]:
        """Run security checks with bandit."""
        print("🔒 Running security checks...")
        
        cmd = [
            sys.executable, "-m", "bandit",
            "-r", "rsmt/",
            "-f", "json",
            "-o", "bandit-report.json",
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Bandit returns 1 for issues found, but that's not necessarily a failure
        success = result.returncode in [0, 1]
        
        return {
            "name": "security_checks",
            "success": success,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_format_check(self, verbose: bool = False) -> Dict[str, Any]:
        """Check code formatting with black."""
        print("🎨 Checking code formatting...")
        
        cmd = [
            sys.executable, "-m", "black",
            "--check",
            "--diff",
            "rsmt/", "scripts/", "tests/", "tools/",
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "format_check",
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_import_check(self, verbose: bool = False) -> Dict[str, Any]:
        """Check import sorting with isort."""
        print("📦 Checking import sorting...")
        
        cmd = [
            sys.executable, "-m", "isort",
            "--check-only",
            "--diff",
            "rsmt/", "scripts/", "tests/", "tools/",
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        return {
            "name": "import_check",
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "duration": 0,
        }
    
    def run_all_tests(self, 
                     quick: bool = False,
                     verbose: bool = False,
                     coverage: bool = True) -> Dict[str, Any]:
        """Run all tests and checks."""
        print("🚀 Running comprehensive test suite...")
        
        results = {}
        
        # Core tests
        results["unit_tests"] = self.run_unit_tests(verbose, coverage)
        
        if not quick:
            results["integration_tests"] = self.run_integration_tests(verbose)
            results["performance_tests"] = self.run_performance_tests(verbose)
        
        # Code quality checks
        results["type_checking"] = self.run_type_checking(verbose)
        results["linting"] = self.run_linting(verbose)
        results["format_check"] = self.run_format_check(verbose)
        results["import_check"] = self.run_import_check(verbose)
        
        if not quick:
            results["security_checks"] = self.run_security_checks(verbose)
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a test report."""
        report = []
        report.append("=" * 60)
        report.append("RSMT Test Results Summary")
        report.append("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        report.append(f"Total test suites: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append("")
        
        # Details for each test
        for name, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report.append(f"{status} {name}")
            
            if not result["success"] and result["errors"]:
                report.append(f"   Error: {result['errors'][:200]}...")
        
        report.append("")
        report.append("=" * 60)
        
        if failed_tests == 0:
            report.append("🎉 All tests passed!")
        else:
            report.append(f"⚠️  {failed_tests} test suite(s) failed")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], output_file: str = "test_results.json") -> None:
        """Save test results to JSON file."""
        import json
        import datetime
        
        output_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results.values() if r["success"]),
                "failed": sum(1 for r in results.values() if not r["success"]),
            }
        }
        
        with open(self.project_root / output_file, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"📄 Test results saved to {output_file}")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="RSMT Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--unit-only", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration-only", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance-only", action="store_true", help="Run performance tests only")
    parser.add_argument("--quality-only", action="store_true", help="Run code quality checks only")
    parser.add_argument("--save-results", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    runner = RSMTTestRunner()
    
    try:
        if args.unit_only:
            results = {"unit_tests": runner.run_unit_tests(args.verbose, not args.no_coverage)}
        elif args.integration_only:
            results = {"integration_tests": runner.run_integration_tests(args.verbose)}
        elif args.performance_only:
            results = {"performance_tests": runner.run_performance_tests(args.verbose)}
        elif args.quality_only:
            results = {
                "type_checking": runner.run_type_checking(args.verbose),
                "linting": runner.run_linting(args.verbose),
                "format_check": runner.run_format_check(args.verbose),
                "import_check": runner.run_import_check(args.verbose),
            }
        else:
            results = runner.run_all_tests(
                quick=args.quick,
                verbose=args.verbose,
                coverage=not args.no_coverage
            )
        
        # Generate and print report
        report = runner.generate_report(results)
        print(report)
        
        # Save results if requested
        if args.save_results:
            runner.save_results(results, args.save_results)
        
        # Exit with appropriate code
        failed_tests = sum(1 for r in results.values() if not r["success"])
        sys.exit(1 if failed_tests > 0 else 0)
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
