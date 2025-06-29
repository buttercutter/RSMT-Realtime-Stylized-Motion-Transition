"""
RSMT CI/CD Metrics Collector

This script collects and analyzes CI/CD pipeline metrics for performance monitoring,
trend analysis, and optimization recommendations.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics
import os


class CICDMetricsCollector:
    """Collects and analyzes CI/CD pipeline metrics."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'performance': {},
            'quality': {},
            'reliability': {},
            'trends': {},
            'recommendations': []
        }
    
    def collect_all_metrics(self) -> Dict:
        """Collect comprehensive CI/CD metrics."""
        print("📊 Collecting CI/CD Metrics...")
        
        # Performance metrics
        self._collect_build_metrics()
        self._collect_test_metrics()
        self._collect_deployment_metrics()
        
        # Quality metrics
        self._collect_code_quality_metrics()
        self._collect_coverage_metrics()
        self._collect_security_metrics()
        
        # Reliability metrics
        self._collect_reliability_metrics()
        
        # Trend analysis
        self._analyze_trends()
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.metrics
    
    def _collect_build_metrics(self):
        """Collect build performance metrics."""
        print("  🏗️ Collecting build metrics...")
        
        build_metrics = {
            'docker_build_time': None,
            'dependency_install_time': None,
            'image_size': None,
            'cache_hit_rate': None
        }
        
        # Measure Docker build time
        dockerfile = self.project_root / 'Dockerfile'
        if dockerfile.exists():
            try:
                start_time = time.time()
                result = subprocess.run([
                    'docker', 'build', '--no-cache', '-t', 'rsmt:metrics-test', '.'
                ], capture_output=True, text=True, timeout=300, cwd=self.project_root)
                
                if result.returncode == 0:
                    build_metrics['docker_build_time'] = time.time() - start_time
                    
                    # Get image size
                    size_result = subprocess.run([
                        'docker', 'images', 'rsmt:metrics-test', '--format', '{{.Size}}'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if size_result.returncode == 0:
                        build_metrics['image_size'] = size_result.stdout.strip()
                    
                    # Cleanup test image
                    subprocess.run(['docker', 'rmi', 'rsmt:metrics-test'], 
                                 capture_output=True, timeout=30)
                
            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"    ⚠️ Docker build measurement failed: {e}")
        
        # Measure dependency install time
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--dry-run', '--quiet', '.'
            ], capture_output=True, text=True, timeout=60, cwd=self.project_root)
            
            if result.returncode == 0:
                build_metrics['dependency_install_time'] = time.time() - start_time
        
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"    ⚠️ Dependency install measurement failed: {e}")
        
        self.metrics['performance']['build'] = build_metrics
    
    def _collect_test_metrics(self):
        """Collect test execution metrics."""
        print("  🧪 Collecting test metrics...")
        
        test_metrics = {
            'total_tests': 0,
            'test_execution_time': None,
            'test_categories': {},
            'parallel_speedup': None
        }
        
        # Count total tests
        test_dir = self.project_root / 'tests'
        if test_dir.exists():
            test_files = list(test_dir.rglob('test_*.py'))
            test_metrics['total_tests'] = len(test_files)
            
            # Categorize tests
            categories = ['unit', 'integration', 'benchmark', 'gpu']
            for category in categories:
                category_files = list(test_dir.rglob(f'*{category}*/test_*.py'))
                category_files.extend(list(test_dir.rglob(f'test_*{category}*.py')))
                test_metrics['test_categories'][category] = len(category_files)
        
        # Measure test execution time
        try:
            start_time = time.time()
            result = subprocess.run([
                'python', '-m', 'pytest', '--co', '-q'
            ], capture_output=True, text=True, timeout=60, cwd=self.project_root)
            
            if result.returncode == 0:
                # Parse test count from pytest output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'tests collected' in line:
                        try:
                            count = int(line.split()[0])
                            test_metrics['total_tests'] = max(test_metrics['total_tests'], count)
                        except (ValueError, IndexError):
                            pass
            
            # Quick test run for timing
            result = subprocess.run([
                'python', '-m', 'pytest', '--maxfail=1', '-x'
            ], capture_output=True, text=True, timeout=300, cwd=self.project_root)
            
            test_metrics['test_execution_time'] = time.time() - start_time
            
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"    ⚠️ Test measurement failed: {e}")
        
        self.metrics['performance']['tests'] = test_metrics
    
    def _collect_deployment_metrics(self):
        """Collect deployment-related metrics."""
        print("  🚀 Collecting deployment metrics...")
        
        deployment_metrics = {
            'package_size': None,
            'startup_time': None,
            'memory_usage': None,
            'cpu_usage': None
        }
        
        # Estimate package size
        try:
            result = subprocess.run([
                'python', 'setup.py', 'sdist', '--dry-run'
            ], capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            # Alternative: check built package if exists
            dist_dir = self.project_root / 'dist'
            if dist_dir.exists():
                package_files = list(dist_dir.glob('*.tar.gz')) + list(dist_dir.glob('*.whl'))
                if package_files:
                    latest_package = max(package_files, key=lambda p: p.stat().st_mtime)
                    deployment_metrics['package_size'] = latest_package.stat().st_size
        
        except Exception as e:
            print(f"    ⚠️ Package size measurement failed: {e}")
        
        # Test import time (proxy for startup time)
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, '-c', 'import rsmt'
            ], capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            if result.returncode == 0:
                deployment_metrics['startup_time'] = time.time() - start_time
        
        except Exception as e:
            print(f"    ⚠️ Import time measurement failed: {e}")
        
        self.metrics['performance']['deployment'] = deployment_metrics
    
    def _collect_code_quality_metrics(self):
        """Collect code quality metrics."""
        print("  🔍 Collecting code quality metrics...")
        
        quality_metrics = {
            'lines_of_code': 0,
            'complexity_score': None,
            'maintainability_index': None,
            'technical_debt': {},
            'linting_issues': {}
        }
        
        # Count lines of code
        src_dirs = ['rsmt', 'src']
        for src_dir in src_dirs:
            src_path = self.project_root / src_dir
            if src_path.exists():
                py_files = list(src_path.rglob('*.py'))
                total_lines = 0
                for py_file in py_files:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except Exception:
                        continue
                quality_metrics['lines_of_code'] = total_lines
                break
        
        # Run linting tools
        linting_tools = {
            'flake8': ['flake8', '--statistics'],
            'mypy': ['mypy', '--show-error-codes'],
            'bandit': ['bandit', '-r', '.', '-f', 'json']
        }
        
        for tool, command in linting_tools.items():
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=60, cwd=self.project_root
                )
                
                if tool == 'flake8':
                    # Parse flake8 statistics
                    lines = result.stdout.split('\n')
                    error_count = 0
                    for line in lines:
                        if line.strip() and line[0].isdigit():
                            try:
                                count = int(line.split()[0])
                                error_count += count
                            except (ValueError, IndexError):
                                pass
                    quality_metrics['linting_issues'][tool] = error_count
                
                elif tool == 'mypy':
                    # Count mypy errors
                    error_lines = [line for line in result.stdout.split('\n') if 'error:' in line]
                    quality_metrics['linting_issues'][tool] = len(error_lines)
                
                elif tool == 'bandit':
                    # Parse bandit JSON output
                    try:
                        bandit_data = json.loads(result.stdout)
                        metrics = bandit_data.get('metrics', {})
                        quality_metrics['linting_issues'][tool] = {
                            'high': len(metrics.get('_totals', {}).get('SEVERITY.HIGH', [])),
                            'medium': len(metrics.get('_totals', {}).get('SEVERITY.MEDIUM', [])),
                            'low': len(metrics.get('_totals', {}).get('SEVERITY.LOW', []))
                        }
                    except json.JSONDecodeError:
                        quality_metrics['linting_issues'][tool] = 'parse_error'
            
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                quality_metrics['linting_issues'][tool] = f"error: {str(e)}"
        
        self.metrics['quality']['code'] = quality_metrics
    
    def _collect_coverage_metrics(self):
        """Collect test coverage metrics."""
        print("  📊 Collecting coverage metrics...")
        
        coverage_metrics = {
            'overall_coverage': None,
            'branch_coverage': None,
            'function_coverage': None,
            'uncovered_lines': 0,
            'coverage_trend': None
        }
        
        try:
            # Run coverage
            subprocess.run(['coverage', 'run', '-m', 'pytest'], 
                         capture_output=True, timeout=300, cwd=self.project_root)
            
            # Get coverage report
            result = subprocess.run(['coverage', 'report', '--show-missing'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'TOTAL' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            try:
                                coverage_str = parts[-1].replace('%', '')
                                coverage_metrics['overall_coverage'] = float(coverage_str)
                                
                                # Extract uncovered lines count
                                if len(parts) >= 5:
                                    uncovered = parts[-2]
                                    if uncovered.isdigit():
                                        coverage_metrics['uncovered_lines'] = int(uncovered)
                            except (ValueError, IndexError):
                                pass
                        break
            
            # Get detailed coverage data
            result = subprocess.run(['coverage', 'json'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                coverage_file = self.project_root / 'coverage.json'
                if coverage_file.exists():
                    try:
                        with open(coverage_file) as f:
                            coverage_data = json.load(f)
                        
                        totals = coverage_data.get('totals', {})
                        coverage_metrics['branch_coverage'] = totals.get('percent_covered_display')
                        
                        # Calculate function coverage
                        files_data = coverage_data.get('files', {})
                        total_functions = sum(
                            len(data.get('summary', {}).get('missing_lines', [])) 
                            for data in files_data.values()
                        )
                        
                        coverage_file.unlink()  # Cleanup
                        
                    except Exception as e:
                        print(f"    ⚠️ Failed to parse coverage JSON: {e}")
        
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"    ⚠️ Coverage measurement failed: {e}")
        
        self.metrics['quality']['coverage'] = coverage_metrics
    
    def _collect_security_metrics(self):
        """Collect security-related metrics."""
        print("  🛡️ Collecting security metrics...")
        
        security_metrics = {
            'vulnerabilities': {},
            'security_score': None,
            'dependency_audit': {},
            'secrets_detected': 0
        }
        
        # Run safety check
        try:
            result = subprocess.run(['safety', 'check', '--json'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                safety_data = json.loads(result.stdout)
                security_metrics['vulnerabilities']['dependencies'] = len(safety_data)
            else:
                # Parse text output if JSON fails
                vuln_count = result.stdout.count('vulnerability found')
                security_metrics['vulnerabilities']['dependencies'] = vuln_count
        
        except Exception as e:
            security_metrics['vulnerabilities']['dependencies'] = f"error: {str(e)}"
        
        # Run bandit security scan
        try:
            result = subprocess.run(['bandit', '-r', '.', '-f', 'json'], 
                                  capture_output=True, text=True, timeout=60, cwd=self.project_root)
            
            if result.returncode in [0, 1]:  # 1 means issues found but scan completed
                try:
                    bandit_data = json.loads(result.stdout)
                    results = bandit_data.get('results', [])
                    
                    severity_counts = {'high': 0, 'medium': 0, 'low': 0}
                    for issue in results:
                        severity = issue.get('issue_severity', '').lower()
                        if severity in severity_counts:
                            severity_counts[severity] += 1
                    
                    security_metrics['vulnerabilities']['code'] = severity_counts
                    
                except json.JSONDecodeError:
                    security_metrics['vulnerabilities']['code'] = 'parse_error'
        
        except Exception as e:
            security_metrics['vulnerabilities']['code'] = f"error: {str(e)}"
        
        # Check for secrets
        try:
            result = subprocess.run(['detect-secrets', 'scan', '--baseline', '.secrets.baseline'], 
                                  capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            if result.returncode == 0:
                try:
                    secrets_data = json.loads(result.stdout)
                    results = secrets_data.get('results', {})
                    total_secrets = sum(len(file_secrets) for file_secrets in results.values())
                    security_metrics['secrets_detected'] = total_secrets
                except json.JSONDecodeError:
                    pass
        
        except Exception as e:
            print(f"    ⚠️ Secrets detection failed: {e}")
        
        self.metrics['quality']['security'] = security_metrics
    
    def _collect_reliability_metrics(self):
        """Collect reliability and stability metrics."""
        print("  🔧 Collecting reliability metrics...")
        
        reliability_metrics = {
            'test_stability': None,
            'error_rate': None,
            'performance_consistency': None,
            'dependency_health': {}
        }
        
        # Analyze test stability (multiple runs)
        try:
            success_count = 0
            total_runs = 3
            execution_times = []
            
            for i in range(total_runs):
                start_time = time.time()
                result = subprocess.run([
                    'python', '-m', 'pytest', '--maxfail=1', '-x', '-q'
                ], capture_output=True, text=True, timeout=180, cwd=self.project_root)
                
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                
                if result.returncode == 0:
                    success_count += 1
            
            reliability_metrics['test_stability'] = success_count / total_runs
            
            if execution_times:
                avg_time = statistics.mean(execution_times)
                std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
                reliability_metrics['performance_consistency'] = {
                    'average_time': avg_time,
                    'standard_deviation': std_dev,
                    'coefficient_variation': std_dev / avg_time if avg_time > 0 else 0
                }
        
        except Exception as e:
            print(f"    ⚠️ Reliability testing failed: {e}")
        
        # Check dependency health
        try:
            result = subprocess.run(['pip', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            
            reliability_metrics['dependency_health']['conflicts'] = result.returncode != 0
            if result.returncode != 0:
                reliability_metrics['dependency_health']['issues'] = result.stdout
        
        except Exception as e:
            reliability_metrics['dependency_health']['error'] = str(e)
        
        self.metrics['reliability'] = reliability_metrics
    
    def _analyze_trends(self):
        """Analyze trends by comparing with historical data."""
        print("  📈 Analyzing trends...")
        
        trends = {
            'historical_comparison': None,
            'performance_trend': None,
            'quality_trend': None
        }
        
        # Look for historical metrics files
        metrics_dir = self.project_root / 'metrics'
        if metrics_dir.exists():
            metric_files = sorted(metrics_dir.glob('metrics_*.json'))
            
            if len(metric_files) >= 2:
                try:
                    # Load recent historical data
                    with open(metric_files[-1]) as f:
                        recent_metrics = json.load(f)
                    
                    # Compare key metrics
                    current_coverage = self.metrics.get('quality', {}).get('coverage', {}).get('overall_coverage')
                    recent_coverage = recent_metrics.get('quality', {}).get('coverage', {}).get('overall_coverage')
                    
                    if current_coverage and recent_coverage:
                        coverage_change = current_coverage - recent_coverage
                        trends['quality_trend'] = {
                            'coverage_change': coverage_change,
                            'improving': coverage_change > 0
                        }
                    
                    # Compare build times
                    current_build_time = self.metrics.get('performance', {}).get('build', {}).get('docker_build_time')
                    recent_build_time = recent_metrics.get('performance', {}).get('build', {}).get('docker_build_time')
                    
                    if current_build_time and recent_build_time:
                        time_change = current_build_time - recent_build_time
                        trends['performance_trend'] = {
                            'build_time_change': time_change,
                            'improving': time_change < 0  # Lower is better
                        }
                
                except Exception as e:
                    trends['historical_comparison'] = f"error: {str(e)}"
        
        self.metrics['trends'] = trends
    
    def _generate_recommendations(self):
        """Generate recommendations based on collected metrics."""
        recommendations = []
        
        # Performance recommendations
        build_time = self.metrics.get('performance', {}).get('build', {}).get('docker_build_time')
        if build_time and build_time > 300:  # 5 minutes
            recommendations.append(f"Build time is {build_time:.1f}s - consider optimizing Dockerfile layers")
        
        test_time = self.metrics.get('performance', {}).get('tests', {}).get('test_execution_time')
        if test_time and test_time > 120:  # 2 minutes
            recommendations.append(f"Test execution time is {test_time:.1f}s - consider parallel test execution")
        
        # Quality recommendations
        coverage = self.metrics.get('quality', {}).get('coverage', {}).get('overall_coverage')
        if coverage and coverage < 80:
            recommendations.append(f"Test coverage is {coverage}% - increase to ≥80%")
        
        # Security recommendations
        vulnerabilities = self.metrics.get('quality', {}).get('security', {}).get('vulnerabilities', {})
        dep_vulns = vulnerabilities.get('dependencies', 0)
        if isinstance(dep_vulns, int) and dep_vulns > 0:
            recommendations.append(f"Found {dep_vulns} dependency vulnerabilities - update packages")
        
        code_vulns = vulnerabilities.get('code', {})
        if isinstance(code_vulns, dict):
            high_vulns = code_vulns.get('high', 0)
            if high_vulns > 0:
                recommendations.append(f"Found {high_vulns} high-severity security issues in code")
        
        # Reliability recommendations
        stability = self.metrics.get('reliability', {}).get('test_stability')
        if stability and stability < 0.9:
            recommendations.append(f"Test stability is {stability:.1%} - investigate flaky tests")
        
        self.metrics['recommendations'] = recommendations
    
    def save_metrics(self, output_file: Optional[Path] = None):
        """Save metrics to file with timestamp."""
        if output_file is None:
            metrics_dir = self.project_root / 'metrics'
            metrics_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = metrics_dir / f'metrics_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"💾 Metrics saved to {output_file}")
        return output_file
    
    def print_summary(self):
        """Print a human-readable summary of the metrics."""
        print("\n" + "="*60)
        print("📊 CI/CD Metrics Summary")
        print("="*60)
        print(f"Timestamp: {self.metrics['timestamp']}")
        
        # Performance metrics
        print("\n🚀 Performance Metrics:")
        perf = self.metrics.get('performance', {})
        
        build = perf.get('build', {})
        if build.get('docker_build_time'):
            print(f"  Docker Build Time: {build['docker_build_time']:.1f}s")
        if build.get('image_size'):
            print(f"  Docker Image Size: {build['image_size']}")
        
        tests = perf.get('tests', {})
        if tests.get('total_tests'):
            print(f"  Total Tests: {tests['total_tests']}")
        if tests.get('test_execution_time'):
            print(f"  Test Execution Time: {tests['test_execution_time']:.1f}s")
        
        # Quality metrics
        print("\n🔍 Quality Metrics:")
        quality = self.metrics.get('quality', {})
        
        code = quality.get('code', {})
        if code.get('lines_of_code'):
            print(f"  Lines of Code: {code['lines_of_code']:,}")
        
        coverage = quality.get('coverage', {})
        if coverage.get('overall_coverage'):
            print(f"  Test Coverage: {coverage['overall_coverage']:.1f}%")
        
        security = quality.get('security', {})
        vulns = security.get('vulnerabilities', {})
        if 'dependencies' in vulns:
            print(f"  Dependency Vulnerabilities: {vulns['dependencies']}")
        if isinstance(vulns.get('code'), dict):
            total_code_vulns = sum(vulns['code'].values())
            print(f"  Code Security Issues: {total_code_vulns}")
        
        # Reliability metrics
        print("\n🔧 Reliability Metrics:")
        reliability = self.metrics.get('reliability', {})
        if reliability.get('test_stability'):
            print(f"  Test Stability: {reliability['test_stability']:.1%}")
        
        # Recommendations
        if self.metrics.get('recommendations'):
            print(f"\n💡 Recommendations ({len(self.metrics['recommendations'])}):")
            for i, rec in enumerate(self.metrics['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Main function to collect CI/CD metrics."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RSMT CI/CD Metrics Collector")
    parser.add_argument('--json', action='store_true', help="Output results in JSON format")
    parser.add_argument('--output', type=str, help="Save results to specific file")
    parser.add_argument('--project-root', type=str, help="Project root directory")
    parser.add_argument('--save', action='store_true', help="Save metrics with timestamp")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    
    # Collect metrics
    collector = CICDMetricsCollector(project_root)
    metrics = collector.collect_all_metrics()
    
    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        collector.print_summary()
    
    # Save metrics
    if args.save or args.output:
        output_file = Path(args.output) if args.output else None
        collector.save_metrics(output_file)


if __name__ == "__main__":
    main()
