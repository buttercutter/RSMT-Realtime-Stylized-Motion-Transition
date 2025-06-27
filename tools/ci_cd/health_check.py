"""
RSMT CI/CD Health Check Script

This script performs comprehensive health checks on the CI/CD pipeline
and provides actionable insights for maintaining optimal performance.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class CICDHealthChecker:
    """Comprehensive health checker for RSMT CI/CD pipeline."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {},
            'recommendations': [],
            'critical_issues': [],
            'warnings': []
        }
    
    def run_all_checks(self) -> Dict:
        """Run all health checks and return comprehensive results."""
        print("🔍 Running CI/CD Health Checks...")
        
        # Core infrastructure checks
        self._check_github_actions()
        self._check_pre_commit_hooks()
        self._check_docker_setup()
        self._check_dependencies()
        
        # Code quality checks
        self._check_test_coverage()
        self._check_code_quality_tools()
        self._check_security_setup()
        
        # Performance checks
        self._check_build_performance()
        self._check_test_performance()
        
        # Documentation checks
        self._check_documentation()
        
        # Environment checks
        self._check_environment_setup()
        
        # Calculate overall status
        self._calculate_overall_status()
        
        return self.results
    
    def _check_github_actions(self):
        """Check GitHub Actions workflow configuration."""
        print("  📋 Checking GitHub Actions...")
        
        workflow_path = self.project_root / '.github' / 'workflows'
        checks = {
            'workflow_files_exist': False,
            'main_workflow_valid': False,
            'release_workflow_valid': False,
            'secrets_documented': False
        }
        
        if workflow_path.exists():
            workflows = list(workflow_path.glob('*.yml')) + list(workflow_path.glob('*.yaml'))
            checks['workflow_files_exist'] = len(workflows) > 0
            
            # Check main CI/CD workflow
            ci_cd_file = workflow_path / 'ci-cd.yml'
            if ci_cd_file.exists():
                try:
                    with open(ci_cd_file) as f:
                        workflow = yaml.safe_load(f)
                    
                    # Validate essential components
                    has_triggers = 'on' in workflow
                    has_jobs = 'jobs' in workflow
                    has_test_job = any('test' in job_name.lower() for job_name in workflow.get('jobs', {}))
                    
                    checks['main_workflow_valid'] = has_triggers and has_jobs and has_test_job
                    
                except Exception as e:
                    self.results['warnings'].append(f"Failed to parse ci-cd.yml: {e}")
            
            # Check release workflow
            release_file = workflow_path / 'release.yml'
            if release_file.exists():
                checks['release_workflow_valid'] = True
        
        self.results['checks']['github_actions'] = checks
        
        if not checks['workflow_files_exist']:
            self.results['critical_issues'].append("No GitHub Actions workflows found")
    
    def _check_pre_commit_hooks(self):
        """Check pre-commit hooks configuration."""
        print("  🔗 Checking pre-commit hooks...")
        
        pre_commit_file = self.project_root / '.pre-commit-config.yaml'
        checks = {
            'config_exists': pre_commit_file.exists(),
            'hooks_installed': False,
            'essential_hooks_present': False
        }
        
        if checks['config_exists']:
            try:
                with open(pre_commit_file) as f:
                    config = yaml.safe_load(f)
                
                # Check for essential hooks
                essential_hooks = {'black', 'isort', 'flake8', 'mypy', 'bandit'}
                found_hooks = set()
                
                for repo in config.get('repos', []):
                    for hook in repo.get('hooks', []):
                        found_hooks.add(hook.get('id', ''))
                
                checks['essential_hooks_present'] = essential_hooks.issubset(found_hooks)
                
            except Exception as e:
                self.results['warnings'].append(f"Failed to parse pre-commit config: {e}")
        
        # Check if hooks are installed
        try:
            result = subprocess.run(['pre-commit', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                checks['hooks_installed'] = True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.results['checks']['pre_commit'] = checks
        
        if not checks['config_exists']:
            self.results['critical_issues'].append("Pre-commit configuration missing")
    
    def _check_docker_setup(self):
        """Check Docker configuration."""
        print("  🐳 Checking Docker setup...")
        
        dockerfile = self.project_root / 'Dockerfile'
        checks = {
            'dockerfile_exists': dockerfile.exists(),
            'multistage_build': False,
            'security_practices': False,
            'health_check': False
        }
        
        if checks['dockerfile_exists']:
            try:
                with open(dockerfile) as f:
                    content = f.read()
                
                # Check for multi-stage build
                checks['multistage_build'] = 'AS ' in content.upper()
                
                # Check for security practices
                security_indicators = ['USER ', 'COPY --chown', 'RUN groupadd', 'RUN useradd']
                checks['security_practices'] = any(indicator in content for indicator in security_indicators)
                
                # Check for health check
                checks['health_check'] = 'HEALTHCHECK' in content
                
            except Exception as e:
                self.results['warnings'].append(f"Failed to analyze Dockerfile: {e}")
        
        # Check Docker availability
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            checks['docker_available'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            checks['docker_available'] = False
        
        self.results['checks']['docker'] = checks
    
    def _check_dependencies(self):
        """Check dependency management."""
        print("  📦 Checking dependencies...")
        
        pyproject_file = self.project_root / 'pyproject.toml'
        requirements_file = self.project_root / 'requirements.txt'
        
        checks = {
            'modern_packaging': pyproject_file.exists(),
            'requirements_exist': requirements_file.exists(),
            'dev_dependencies': False,
            'version_pinning': False
        }
        
        if checks['modern_packaging']:
            try:
                import tomli
                with open(pyproject_file, 'rb') as f:
                    pyproject_data = tomli.load(f)
                
                # Check for development dependencies
                checks['dev_dependencies'] = 'dev' in pyproject_data.get('project', {}).get('optional-dependencies', {})
                
            except Exception as e:
                self.results['warnings'].append(f"Failed to parse pyproject.toml: {e}")
        
        # Check for security vulnerabilities
        try:
            result = subprocess.run(['safety', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            checks['security_check'] = result.returncode == 0
            if result.returncode != 0:
                self.results['warnings'].append("Security vulnerabilities found in dependencies")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            checks['security_check'] = None
        
        self.results['checks']['dependencies'] = checks
    
    def _check_test_coverage(self):
        """Check test coverage configuration and current status."""
        print("  📊 Checking test coverage...")
        
        checks = {
            'coverage_configured': False,
            'coverage_threshold': False,
            'current_coverage': None
        }
        
        # Check if coverage is configured in pyproject.toml
        pyproject_file = self.project_root / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                import tomli
                with open(pyproject_file, 'rb') as f:
                    data = tomli.load(f)
                
                coverage_config = data.get('tool', {}).get('coverage', {})
                checks['coverage_configured'] = bool(coverage_config)
                
                # Check for coverage threshold
                report_config = coverage_config.get('report', {})
                fail_under = report_config.get('fail_under')
                checks['coverage_threshold'] = fail_under is not None and fail_under >= 80
                
            except Exception as e:
                self.results['warnings'].append(f"Failed to check coverage config: {e}")
        
        # Try to get current coverage
        try:
            result = subprocess.run(['coverage', 'report', '--show-missing'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Parse coverage percentage from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'TOTAL' in line:
                        parts = line.split()
                        if len(parts) >= 4 and '%' in parts[-1]:
                            coverage_str = parts[-1].replace('%', '')
                            try:
                                checks['current_coverage'] = float(coverage_str)
                            except ValueError:
                                pass
                        break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.results['checks']['test_coverage'] = checks
        
        if checks['current_coverage'] and checks['current_coverage'] < 80:
            self.results['warnings'].append(f"Test coverage is {checks['current_coverage']}% (target: ≥80%)")
    
    def _check_code_quality_tools(self):
        """Check code quality tools configuration."""
        print("  🔍 Checking code quality tools...")
        
        tools = ['black', 'isort', 'flake8', 'mypy', 'bandit']
        checks = {}
        
        for tool in tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                checks[f'{tool}_available'] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                checks[f'{tool}_available'] = False
        
        self.results['checks']['code_quality'] = checks
        
        missing_tools = [tool for tool in tools if not checks.get(f'{tool}_available', False)]
        if missing_tools:
            self.results['warnings'].append(f"Missing code quality tools: {', '.join(missing_tools)}")
    
    def _check_security_setup(self):
        """Check security scanning setup."""
        print("  🛡️ Checking security setup...")
        
        checks = {
            'bandit_configured': False,
            'safety_available': False,
            'secrets_baseline': False
        }
        
        # Check for bandit configuration
        bandit_configs = ['.bandit', 'bandit.yaml', 'pyproject.toml']
        for config_file in bandit_configs:
            if (self.project_root / config_file).exists():
                checks['bandit_configured'] = True
                break
        
        # Check for safety
        try:
            result = subprocess.run(['safety', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            checks['safety_available'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for secrets baseline
        secrets_baseline = self.project_root / '.secrets.baseline'
        checks['secrets_baseline'] = secrets_baseline.exists()
        
        self.results['checks']['security'] = checks
    
    def _check_build_performance(self):
        """Check build performance metrics."""
        print("  ⚡ Checking build performance...")
        
        checks = {
            'docker_build_time': None,
            'dependency_install_time': None,
            'cache_strategy': False
        }
        
        # Check for build optimization strategies
        dockerfile = self.project_root / 'Dockerfile'
        if dockerfile.exists():
            try:
                with open(dockerfile) as f:
                    content = f.read()
                
                # Look for caching strategies
                cache_indicators = ['--mount=type=cache', 'pip install --cache-dir', 'BuildKit']
                checks['cache_strategy'] = any(indicator in content for indicator in cache_indicators)
                
            except Exception as e:
                self.results['warnings'].append(f"Failed to analyze Docker caching: {e}")
        
        self.results['checks']['build_performance'] = checks
    
    def _check_test_performance(self):
        """Check test execution performance."""
        print("  🏃 Checking test performance...")
        
        checks = {
            'parallel_execution': False,
            'test_selection': False,
            'fast_tests_available': False
        }
        
        # Check pytest configuration
        pytest_configs = ['pytest.ini', 'pyproject.toml', 'setup.cfg']
        for config_file in pytest_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        content = f.read()
                    
                    # Check for parallel execution
                    checks['parallel_execution'] = '-n auto' in content or 'pytest-xdist' in content
                    
                    # Check for test markers (for selection)
                    checks['test_selection'] = 'markers' in content or '@pytest.mark' in content
                    
                except Exception as e:
                    self.results['warnings'].append(f"Failed to check pytest config: {e}")
                break
        
        # Check for fast test availability
        test_dir = self.project_root / 'tests'
        if test_dir.exists():
            test_files = list(test_dir.rglob('test_*.py'))
            checks['fast_tests_available'] = len(test_files) > 0
        
        self.results['checks']['test_performance'] = checks
    
    def _check_documentation(self):
        """Check documentation setup and status."""
        print("  📚 Checking documentation...")
        
        docs_dir = self.project_root / 'docs'
        checks = {
            'docs_directory': docs_dir.exists(),
            'sphinx_configured': False,
            'api_docs': False,
            'readme_complete': False
        }
        
        if checks['docs_directory']:
            # Check for Sphinx
            conf_py = docs_dir / 'conf.py'
            checks['sphinx_configured'] = conf_py.exists()
            
            # Check for API documentation
            api_dir = docs_dir / 'api'
            checks['api_docs'] = api_dir.exists()
        
        # Check README completeness
        readme_files = ['README.md', 'ReadMe.md', 'readme.md']
        for readme_name in readme_files:
            readme_path = self.project_root / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path) as f:
                        content = f.read()
                    
                    # Check for essential sections
                    essential_sections = ['installation', 'usage', 'example']
                    sections_found = sum(1 for section in essential_sections 
                                       if section.lower() in content.lower())
                    
                    checks['readme_complete'] = sections_found >= 2
                    
                except Exception as e:
                    self.results['warnings'].append(f"Failed to analyze README: {e}")
                break
        
        self.results['checks']['documentation'] = checks
    
    def _check_environment_setup(self):
        """Check development environment setup."""
        print("  🔧 Checking environment setup...")
        
        checks = {
            'python_version': None,
            'virtual_env': False,
            'git_configured': False,
            'editor_config': False
        }
        
        # Check Python version
        checks['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # Check for virtual environment
        checks['virtual_env'] = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        # Check Git configuration
        try:
            result = subprocess.run(['git', 'config', '--global', 'user.name'], 
                                  capture_output=True, text=True, timeout=5)
            checks['git_configured'] = result.returncode == 0 and bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for editor configuration
        editor_configs = ['.vscode/', '.editorconfig', '.idea/']
        checks['editor_config'] = any((self.project_root / config).exists() for config in editor_configs)
        
        self.results['checks']['environment'] = checks
        
        if not checks['virtual_env']:
            self.results['warnings'].append("Not running in a virtual environment")
    
    def _calculate_overall_status(self):
        """Calculate overall CI/CD health status."""
        total_checks = 0
        passed_checks = 0
        
        for category, checks in self.results['checks'].items():
            for check_name, result in checks.items():
                if isinstance(result, bool):
                    total_checks += 1
                    if result:
                        passed_checks += 1
        
        if total_checks == 0:
            self.results['overall_status'] = 'unknown'
        else:
            success_rate = passed_checks / total_checks
            
            if len(self.results['critical_issues']) > 0:
                self.results['overall_status'] = 'critical'
            elif success_rate >= 0.9:
                self.results['overall_status'] = 'excellent'
            elif success_rate >= 0.8:
                self.results['overall_status'] = 'good'
            elif success_rate >= 0.6:
                self.results['overall_status'] = 'fair'
            else:
                self.results['overall_status'] = 'poor'
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on health check results."""
        recommendations = []
        
        # GitHub Actions recommendations
        if not self.results['checks'].get('github_actions', {}).get('workflow_files_exist', False):
            recommendations.append("Set up GitHub Actions workflows for automated CI/CD")
        
        # Pre-commit recommendations
        if not self.results['checks'].get('pre_commit', {}).get('hooks_installed', False):
            recommendations.append("Install and configure pre-commit hooks: `pre-commit install`")
        
        # Coverage recommendations
        coverage_data = self.results['checks'].get('test_coverage', {})
        if coverage_data.get('current_coverage') and coverage_data['current_coverage'] < 80:
            recommendations.append(f"Increase test coverage from {coverage_data['current_coverage']}% to ≥80%")
        
        # Security recommendations
        security_data = self.results['checks'].get('security', {})
        if not security_data.get('secrets_baseline', False):
            recommendations.append("Set up secrets detection baseline: `detect-secrets scan --baseline .secrets.baseline`")
        
        # Performance recommendations
        build_data = self.results['checks'].get('build_performance', {})
        if not build_data.get('cache_strategy', False):
            recommendations.append("Implement Docker build caching for faster builds")
        
        # Documentation recommendations
        docs_data = self.results['checks'].get('documentation', {})
        if not docs_data.get('sphinx_configured', False):
            recommendations.append("Set up Sphinx for automated documentation generation")
        
        self.results['recommendations'] = recommendations
    
    def print_summary(self):
        """Print a human-readable summary of the health check results."""
        status_emoji = {
            'excellent': '🟢',
            'good': '🟡',
            'fair': '🟠',
            'poor': '🔴',
            'critical': '🚨',
            'unknown': '❓'
        }
        
        print("\n" + "="*60)
        print(f"🏥 CI/CD Health Check Summary")
        print("="*60)
        print(f"Overall Status: {status_emoji.get(self.results['overall_status'], '❓')} {self.results['overall_status'].upper()}")
        print(f"Timestamp: {self.results['timestamp']}")
        
        # Critical issues
        if self.results['critical_issues']:
            print(f"\n🚨 Critical Issues ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"  ❌ {issue}")
        
        # Warnings
        if self.results['warnings']:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"  ⚠️ {warning}")
        
        # Recommendations
        if self.results['recommendations']:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Detailed results
        print(f"\n📊 Detailed Results:")
        for category, checks in self.results['checks'].items():
            print(f"\n  {category.replace('_', ' ').title()}:")
            for check_name, result in checks.items():
                if isinstance(result, bool):
                    status = "✅" if result else "❌"
                    print(f"    {status} {check_name.replace('_', ' ').title()}")
                elif result is not None:
                    print(f"    ℹ️ {check_name.replace('_', ' ').title()}: {result}")
        
        print("\n" + "="*60)


def main():
    """Main function to run CI/CD health checks."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RSMT CI/CD Health Checker")
    parser.add_argument('--json', action='store_true', help="Output results in JSON format")
    parser.add_argument('--output', type=str, help="Save results to file")
    parser.add_argument('--project-root', type=str, help="Project root directory")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    
    # Run health checks
    checker = CICDHealthChecker(project_root)
    results = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        checker.print_summary()
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")
    
    # Exit with appropriate code
    if results['overall_status'] in ['critical', 'poor']:
        sys.exit(1)
    elif results['overall_status'] == 'fair':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
