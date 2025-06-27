#!/usr/bin/env python3
"""
RSMT Development Environment Setup
Automated setup script for RSMT development environment.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Any


class DevEnvironmentSetup:
    """Sets up RSMT development environment."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.python_exe = sys.executable
        
    def run_command(self, cmd: List[str], check: bool = True, cwd: Path = None) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        cwd = cwd or self.project_root
        print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                check=check, 
                capture_output=True, 
                text=True
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            if e.stdout:
                print("STDOUT:", e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            if check:
                raise
            return e
    
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are installed."""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check Git
        try:
            result = self.run_command(["git", "--version"], check=False)
            if result.returncode == 0:
                print("✅ Git available")
            else:
                print("❌ Git not found")
                return False
        except FileNotFoundError:
            print("❌ Git not found")
            return False
        
        # Check if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment detected")
        else:
            print("⚠️  Not in a virtual environment - recommended to use one")
        
        return True
    
    def install_dependencies(self, dev: bool = True, docs: bool = False, all_extras: bool = False) -> None:
        """Install Python dependencies."""
        print("📦 Installing dependencies...")
        
        # Upgrade pip first
        self.run_command([self.python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install package in development mode
        cmd = [self.python_exe, "-m", "pip", "install", "-e", "."]
        
        # Add extras
        extras = []
        if dev:
            extras.append("dev")
        if docs:
            extras.append("docs")
        if all_extras:
            extras.append("all")
        
        if extras:
            cmd[-1] = f".[{','.join(extras)}]"
        
        self.run_command(cmd)
        print("✅ Dependencies installed")
    
    def setup_pre_commit(self) -> None:
        """Setup pre-commit hooks."""
        print("🪝 Setting up pre-commit hooks...")
        
        # Install pre-commit hooks
        self.run_command([self.python_exe, "-m", "pre_commit", "install"])
        
        # Install commit-msg hook for commitizen
        self.run_command([self.python_exe, "-m", "pre_commit", "install", "--hook-type", "commit-msg"])
        
        print("✅ Pre-commit hooks installed")
    
    def setup_ide_config(self) -> None:
        """Setup IDE configuration files."""
        print("⚙️  Setting up IDE configuration...")
        
        # Create .vscode directory and settings
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # VS Code settings
        settings = {
            "python.defaultInterpreterPath": self.python_exe,
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.mypyEnabled": True,
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": ["--line-length=88"],
            "python.sortImports.args": ["--profile=black"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.pytest_cache": True,
                "**/.coverage": True,
                "**/htmlcov": True,
                "**/.mypy_cache": True,
                "**/build": True,
                "**/dist": True,
                "**/*.egg-info": True
            },
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": [
                "tests"
            ],
            "python.testing.unittestEnabled": False,
            "python.testing.autoTestDiscoverOnSaveEnabled": True,
        }
        
        import json
        with open(vscode_dir / "settings.json", "w") as f:
            json.dump(settings, f, indent=2)
        
        # VS Code extensions recommendations
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.black-formatter", 
                "ms-python.isort",
                "ms-python.flake8",
                "ms-python.mypy-type-checker",
                "ms-vscode.test-adapter-converter",
                "ms-vscode.vscode-json",
                "redhat.vscode-yaml",
                "streetsidesoftware.code-spell-checker",
                "github.vscode-pull-request-github",
                "github.copilot",
                "ms-vscode.vscode-github-actions",
            ]
        }
        
        with open(vscode_dir / "extensions.json", "w") as f:
            json.dump(extensions, f, indent=2)
        
        print("✅ IDE configuration created")
    
    def create_env_file(self) -> None:
        """Create environment file template."""
        print("📝 Creating environment file template...")
        
        env_template = """# RSMT Environment Configuration
# Copy this file to .env and customize as needed

# Development settings
RSMT_DEBUG=true
RSMT_LOG_LEVEL=INFO

# Data paths
RSMT_DATA_ROOT=./MotionData
RSMT_OUTPUT_ROOT=./output
RSMT_CACHE_ROOT=./cache

# Training settings
RSMT_DEVICE=auto
RSMT_NUM_WORKERS=4
RSMT_BATCH_SIZE=32

# Web interface settings
RSMT_WEB_HOST=localhost
RSMT_WEB_PORT=5000
RSMT_WEB_DEBUG=true

# Experiment tracking
RSMT_EXPERIMENT_NAME=default
RSMT_EXPERIMENT_VERSION=1.0

# Model checkpoints
RSMT_CHECKPOINT_DIR=./checkpoints
RSMT_SAVE_TOP_K=3

# Visualization
RSMT_VIZ_BACKEND=matplotlib
RSMT_VIZ_DPI=100

# Advanced settings
RSMT_COMPILE_MODE=false
RSMT_MIXED_PRECISION=true
RSMT_GRADIENT_CLIP_VAL=1.0
"""
        
        env_file = self.project_root / ".env.example"
        with open(env_file, "w") as f:
            f.write(env_template)
        
        print("✅ Environment file template created (.env.example)")
    
    def run_initial_tests(self) -> None:
        """Run initial test suite to verify setup."""
        print("🧪 Running initial tests...")
        
        try:
            # Run a subset of tests
            self.run_command([
                self.python_exe, "-m", "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "-x",  # Stop on first failure
                "--timeout=60",
            ])
            print("✅ Initial tests passed")
        except subprocess.CalledProcessError:
            print("⚠️  Some tests failed - this is normal for initial setup")
    
    def create_development_scripts(self) -> None:
        """Create helpful development scripts."""
        print("📜 Creating development scripts...")
        
        scripts_dir = self.project_root / "scripts" / "dev"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Format code script
        format_script = """#!/bin/bash
# Format all Python code
echo "🎨 Formatting code..."
python -m black rsmt scripts tests tools
python -m isort rsmt scripts tests tools
echo "✅ Code formatted"
"""
        
        with open(scripts_dir / "format.sh", "w") as f:
            f.write(format_script)
        
        # Run tests script
        test_script = """#!/bin/bash
# Run comprehensive test suite
echo "🧪 Running tests..."
python -m pytest tests/ -v --cov=rsmt --cov-report=html
echo "✅ Tests completed"
"""
        
        with open(scripts_dir / "test.sh", "w") as f:
            f.write(test_script)
        
        # Build docs script
        docs_script = """#!/bin/bash
# Build documentation
echo "📚 Building documentation..."
cd docs
make clean
make html
echo "✅ Documentation built"
"""
        
        with open(scripts_dir / "docs.sh", "w") as f:
            f.write(docs_script)
        
        # Make scripts executable
        for script in scripts_dir.glob("*.sh"):
            script.chmod(0o755)
        
        print("✅ Development scripts created")
    
    def print_next_steps(self) -> None:
        """Print next steps for the developer."""
        print("\n" + "="*60)
        print("🎉 RSMT Development Environment Setup Complete!")
        print("="*60)
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env and customize")
        print("2. Run initial migration: python tools/migration/migrate_codebase.py")
        print("3. Start development server: python -m rsmt.web.app")
        print("4. Run tests: python -m pytest")
        print("5. Format code: ./scripts/dev/format.sh")
        print("\n🔗 Useful commands:")
        print("• Pre-commit check: pre-commit run --all-files")
        print("• Type checking: mypy rsmt/")
        print("• Security scan: bandit -r rsmt/")
        print("• Build docs: ./scripts/dev/docs.sh")
        print("\n📖 Documentation:")
        print("• Implementation Guide: IMPLEMENTATION_GUIDE.md")
        print("• Quick Reference: QUICK_REFERENCE.md")
        print("• Reorganization Plan: CODEBASE_REORGANIZATION_PLAN.md")
        print("\n💡 Tips:")
        print("• Use 'rsmt --help' to see CLI options")
        print("• Check GitHub Actions for CI/CD status")
        print("• Submit issues at https://github.com/rsmt-project/rsmt/issues")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup RSMT development environment")
    parser.add_argument("--no-dev", action="store_true", help="Skip dev dependencies")
    parser.add_argument("--docs", action="store_true", help="Install docs dependencies")
    parser.add_argument("--all", action="store_true", help="Install all dependencies")
    parser.add_argument("--no-precommit", action="store_true", help="Skip pre-commit setup")
    parser.add_argument("--no-tests", action="store_true", help="Skip initial test run")
    parser.add_argument("--quick", action="store_true", help="Quick setup (minimal checks)")
    
    args = parser.parse_args()
    
    print("🚀 RSMT Development Environment Setup")
    print("=" * 40)
    
    setup = DevEnvironmentSetup()
    
    try:
        # Check prerequisites
        if not args.quick and not setup.check_prerequisites():
            print("❌ Prerequisites check failed")
            sys.exit(1)
        
        # Install dependencies
        setup.install_dependencies(
            dev=not args.no_dev,
            docs=args.docs,
            all_extras=args.all
        )
        
        # Setup pre-commit hooks
        if not args.no_precommit:
            setup.setup_pre_commit()
        
        # Setup IDE configuration
        setup.setup_ide_config()
        
        # Create environment file
        setup.create_env_file()
        
        # Create development scripts
        setup.create_development_scripts()
        
        # Run initial tests
        if not args.no_tests:
            setup.run_initial_tests()
        
        # Print next steps
        setup.print_next_steps()
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
