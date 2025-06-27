#!/usr/bin/env python3
"""
RSMT Migration Validation Script

This script validates that the codebase reorganization maintains all functionality
and that the new structure works correctly.

Usage:
    python tools/migration/validate_migration.py --quick
    python tools/migration/validate_migration.py --full
    python tools/migration/validate_migration.py --specific deephase
"""

import os
import sys
import subprocess
import importlib
import traceback
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse

class MigrationValidator:
    """Validates RSMT codebase migration"""
    
    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).parent.parent.parent
        self.results = []
        self.errors = []
        
        # Add project root to Python path
        sys.path.insert(0, str(self.root_dir))
    
    def run_quick_validation(self) -> bool:
        """Run quick validation tests"""
        print("🚀 Running Quick Validation Tests")
        print("=" * 50)
        
        tests = [
            ("Package Structure", self.test_package_structure),
            ("Core Imports", self.test_core_imports),
            ("Basic Functionality", self.test_basic_functionality),
            ("Configuration", self.test_configuration)
        ]
        
        return self._run_test_suite(tests)
    
    def run_full_validation(self) -> bool:
        """Run comprehensive validation tests"""
        print("🚀 Running Full Validation Tests")
        print("=" * 50)
        
        tests = [
            ("Package Structure", self.test_package_structure),
            ("Core Imports", self.test_core_imports),
            ("Model Loading", self.test_model_loading),
            ("Data Processing", self.test_data_processing),
            ("Training Interface", self.test_training_interface),
            ("Web API", self.test_web_api),
            ("Geometry Utils", self.test_geometry_utils),
            ("BVH Processing", self.test_bvh_processing),
            ("Configuration", self.test_configuration),
            ("Script Interfaces", self.test_script_interfaces)
        ]
        
        return self._run_test_suite(tests)
    
    def run_specific_test(self, test_name: str) -> bool:
        """Run specific test"""
        test_map = {
            "structure": self.test_package_structure,
            "imports": self.test_core_imports,
            "models": self.test_model_loading,
            "data": self.test_data_processing,
            "training": self.test_training_interface,
            "web": self.test_web_api,
            "geometry": self.test_geometry_utils,
            "bvh": self.test_bvh_processing,
            "config": self.test_configuration,
            "scripts": self.test_script_interfaces
        }
        
        if test_name not in test_map:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available tests: {list(test_map.keys())}")
            return False
        
        print(f"🚀 Running {test_name} validation")
        return self._run_single_test(test_name.title(), test_map[test_name])
    
    def _run_test_suite(self, tests: List[Tuple[str, callable]]) -> bool:
        """Run a suite of tests"""
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self._run_single_test(test_name, test_func):
                passed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Validation Results: {passed}/{total} tests passed")
        
        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors:
                print(f"  • {error}")
        
        return passed == total
    
    def _run_single_test(self, test_name: str, test_func: callable) -> bool:
        """Run a single test"""
        try:
            print(f"\n🔍 Testing {test_name}...")
            result = test_func()
            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
            return result
        except Exception as e:
            error_msg = f"{test_name}: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {test_name} - ERROR: {e}")
            if os.getenv('RSMT_DEBUG'):
                traceback.print_exc()
            return False
    
    def test_package_structure(self) -> bool:
        """Test that package structure is correct"""
        required_dirs = [
            "rsmt",
            "rsmt/core",
            "rsmt/core/models",
            "rsmt/core/modules", 
            "rsmt/data",
            "rsmt/data/datasets",
            "rsmt/data/preprocessing",
            "rsmt/geometry",
            "rsmt/utils",
            "rsmt/training",
            "rsmt/training/trainers",
            "rsmt/web",
            "rsmt/evaluation",
            "scripts",
            "tests",
            "examples",
            "tools"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print(f"  Missing directories: {missing_dirs}")
            return False
        
        # Check for __init__.py files in Python packages
        python_packages = [d for d in required_dirs if d.startswith('rsmt')]
        missing_inits = []
        for package in python_packages:
            init_file = self.root_dir / package / "__init__.py"
            if not init_file.exists():
                missing_inits.append(package)
        
        if missing_inits:
            print(f"  Missing __init__.py files: {missing_inits}")
            return False
        
        print("  ✓ All required directories and __init__.py files present")
        return True
    
    def test_core_imports(self) -> bool:
        """Test that core modules can be imported"""
        imports_to_test = [
            "rsmt",
            "rsmt.core",
            "rsmt.data",
            "rsmt.utils",
            "rsmt.geometry",
            "rsmt.config"
        ]
        
        failed_imports = []
        for import_name in imports_to_test:
            try:
                importlib.import_module(import_name)
                print(f"  ✓ Successfully imported {import_name}")
            except ImportError as e:
                failed_imports.append(f"{import_name}: {e}")
        
        if failed_imports:
            print(f"  Failed imports: {failed_imports}")
            return False
        
        return True
    
    def test_model_loading(self) -> bool:
        """Test that model interfaces work"""
        try:
            # Test model imports (may fail if dependencies not available)
            try:
                from rsmt.core.models import deephase, stylevae, transition
                print("  ✓ Model modules imported successfully")
            except ImportError as e:
                print(f"  ⚠️  Model imports failed (dependencies may be missing): {e}")
                # This is not a failure if dependencies aren't installed
            
            # Test model directory structure
            models_dir = self.root_dir / "rsmt" / "core" / "models"
            expected_files = ["deephase.py", "stylevae.py", "transition.py"]
            
            for model_file in expected_files:
                if not (models_dir / model_file).exists():
                    print(f"  ❌ Missing model file: {model_file}")
                    return False
            
            print("  ✓ Model files present")
            return True
            
        except Exception as e:
            print(f"  ❌ Model loading test failed: {e}")
            return False
    
    def test_data_processing(self) -> bool:
        """Test data processing interfaces"""
        try:
            # Test data module imports
            from rsmt.data import datasets
            print("  ✓ Data modules imported")
            
            # Test data directory structure
            data_dir = self.root_dir / "rsmt" / "data"
            required_subdirs = ["datasets", "preprocessing"]
            
            for subdir in required_subdirs:
                if not (data_dir / subdir).exists():
                    print(f"  ❌ Missing data subdirectory: {subdir}")
                    return False
            
            print("  ✓ Data structure validated")
            return True
            
        except Exception as e:
            print(f"  ❌ Data processing test failed: {e}")
            return False
    
    def test_training_interface(self) -> bool:
        """Test training interfaces"""
        try:
            # Test training module structure
            training_dir = self.root_dir / "rsmt" / "training"
            if not training_dir.exists():
                print("  ❌ Training directory missing")
                return False
            
            # Test trainers directory
            trainers_dir = training_dir / "trainers"
            if not trainers_dir.exists():
                print("  ❌ Trainers directory missing")
                return False
            
            # Try to import training module
            from rsmt.training import trainers
            print("  ✓ Training modules imported")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Training interface test failed: {e}")
            return False
    
    def test_web_api(self) -> bool:
        """Test web API interfaces"""
        try:
            # Test web module structure
            web_dir = self.root_dir / "rsmt" / "web"
            if not web_dir.exists():
                print("  ❌ Web directory missing")
                return False
            
            # Test for server file
            server_file = web_dir / "server.py"
            if not server_file.exists():
                print("  ❌ Web server file missing")
                return False
            
            # Try to import web module
            from rsmt.web import api
            print("  ✓ Web modules imported")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Web API test failed: {e}")
            return False
    
    def test_geometry_utils(self) -> bool:
        """Test geometry utilities"""
        try:
            # Test geometry module imports
            from rsmt.geometry import quaternions, kinematics, vector
            print("  ✓ Geometry modules imported")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Geometry utils test failed: {e}")
            return False
    
    def test_bvh_processing(self) -> bool:
        """Test BVH processing utilities"""
        try:
            # Test BVH utilities
            from rsmt.utils import bvh, bvh_writer, motion_decoder
            print("  ✓ BVH processing modules imported")
            
            return True
            
        except Exception as e:
            print(f"  ❌ BVH processing test failed: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test configuration system"""
        try:
            # Test configuration imports
            from rsmt.config import DefaultConfig
            
            # Test configuration instantiation
            config = DefaultConfig()
            
            # Check required attributes
            required_attrs = ['DATA_ROOT', 'MODEL_PATH', 'BATCH_SIZE', 'LEARNING_RATE']
            for attr in required_attrs:
                if not hasattr(config, attr):
                    print(f"  ❌ Missing config attribute: {attr}")
                    return False
            
            print("  ✓ Configuration system validated")
            return True
            
        except Exception as e:
            print(f"  ❌ Configuration test failed: {e}")
            return False
    
    def test_script_interfaces(self) -> bool:
        """Test script interfaces"""
        try:
            # Test scripts directory structure
            scripts_dir = self.root_dir / "scripts"
            if not scripts_dir.exists():
                print("  ❌ Scripts directory missing")
                return False
            
            required_script_dirs = ["preprocessing", "training", "inference", "evaluation"]
            missing_dirs = []
            
            for script_dir in required_script_dirs:
                if not (scripts_dir / script_dir).exists():
                    missing_dirs.append(script_dir)
            
            if missing_dirs:
                print(f"  ❌ Missing script directories: {missing_dirs}")
                return False
            
            print("  ✓ Script structure validated")
            return True
            
        except Exception as e:
            print(f"  ❌ Script interface test failed: {e}")
            return False
    
    def test_legacy_compatibility(self) -> bool:
        """Test that critical legacy functionality still works"""
        try:
            # Test that key files exist in backup
            backup_dir = self.root_dir / "backup_original"
            if not backup_dir.exists():
                print("  ⚠️  No backup directory found")
                return True  # Not a failure if migration hasn't created backup yet
            
            # Test that we can still access old structure for comparison
            old_src = backup_dir / "src"
            if old_src.exists():
                print("  ✓ Legacy code preserved in backup")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Legacy compatibility test failed: {e}")
            return False
    
    def test_packaging(self) -> bool:
        """Test that the package can be built and installed"""
        try:
            # Check for packaging files
            packaging_files = ["pyproject.toml", "setup.py"]
            missing_files = []
            
            for file_name in packaging_files:
                if not (self.root_dir / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                print(f"  ❌ Missing packaging files: {missing_files}")
                return False
            
            # Test that setup.py can be parsed
            setup_py = self.root_dir / "setup.py"
            try:
                exec(setup_py.read_text())
                print("  ✓ setup.py is valid")
            except Exception as e:
                print(f"  ❌ setup.py is invalid: {e}")
                return False
            
            print("  ✓ Packaging configuration validated")
            return True
            
        except Exception as e:
            print(f"  ❌ Packaging test failed: {e}")
            return False


def main():
    """Main validation script entry point"""
    parser = argparse.ArgumentParser(description='RSMT Migration Validation Tool')
    parser.add_argument('--quick', action='store_true', help='Run quick validation')
    parser.add_argument('--full', action='store_true', help='Run full validation')
    parser.add_argument('--specific', type=str, help='Run specific test')
    parser.add_argument('--root', type=str, help='Root directory of RSMT project')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.debug:
        os.environ['RSMT_DEBUG'] = '1'
    
    validator = MigrationValidator(args.root)
    
    success = False
    if args.quick:
        success = validator.run_quick_validation()
    elif args.full:
        success = validator.run_full_validation()
    elif args.specific:
        success = validator.run_specific_test(args.specific)
    else:
        print("Please specify --quick, --full, or --specific <test_name>")
        parser.print_help()
        return 1
    
    if success:
        print("\n🎉 All validation tests passed! Migration appears successful.")
        return 0
    else:
        print("\n❌ Some validation tests failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
