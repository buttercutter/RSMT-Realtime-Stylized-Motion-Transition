#!/usr/bin/env python3
"""
RSMT Setup Script
Backward compatibility setup.py for systems that don't support pyproject.toml
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read version from rsmt/__init__.py
def get_version():
    """Extract version from rsmt/__init__.py."""
    init_file = Path(__file__).parent / "rsmt" / "__init__.py"
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

# Read long description from README
def get_long_description():
    """Read long description from README file."""
    readme_file = Path(__file__).parent / "ReadMe.md"
    if readme_file.exists():
        with open(readme_file, encoding="utf-8") as f:
            return f.read()
    return ""

# Core dependencies
INSTALL_REQUIRES = [
    "torch>=1.12.0",
    "torchvision>=0.13.0", 
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "matplotlib>=3.5.0",
    "pyyaml>=6.0",
    "tqdm>=4.62.0",
    "tensorboard>=2.8.0",
    "lightning>=2.0.0",
    "hydra-core>=1.3.0",
    "omegaconf>=2.3.0",
    "pillow>=8.3.0",
    "opencv-python>=4.5.0",
    "scikit-learn>=1.0.0",
    "pandas>=1.3.0",
    "h5py>=3.6.0",
    "requests>=2.25.0",
]

# Optional dependencies
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-xdist>=3.0.0",
        "pytest-timeout>=2.1.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "bandit>=1.7.0",
        "safety>=2.3.0",
        "pre-commit>=3.0.0",
    ],
    "docs": [
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.2.0",
        "sphinxcontrib-napoleon>=0.7",
        "myst-parser>=0.18.0", 
        "sphinx-autodoc-typehints>=1.19.0",
    ],
    "web": [
        "flask>=2.2.0",
        "flask-cors>=4.0.0",
        "gunicorn>=20.1.0",
        "websockets>=10.4",
    ],
    "benchmark": [
        "pytest-benchmark>=4.0.0",
        "memory-profiler>=0.60.0",
        "psutil>=5.9.0",
    ],
}

# Add 'all' extra that includes everything
EXTRAS_REQUIRE["all"] = list(set(
    dep for deps in EXTRAS_REQUIRE.values() for dep in deps
))

# Console scripts
ENTRY_POINTS = {
    "console_scripts": [
        "rsmt=rsmt.cli:main",
        "rsmt-train=scripts.train:main", 
        "rsmt-preprocess=scripts.preprocess:main",
        "rsmt-demo=scripts.demo:main",
    ],
}

# Package data
PACKAGE_DATA = {
    "rsmt": ["*.yaml", "*.json", "*.txt", "data/**/*"],
}

# Classifiers
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research", 
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10", 
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Multimedia :: Graphics :: 3D Modeling",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# Keywords
KEYWORDS = [
    "machine-learning",
    "deep-learning",
    "computer-graphics", 
    "animation",
    "motion-synthesis",
    "pytorch",
    "neural-networks",
    "character-animation",
]

def check_python_version():
    """Check if Python version is supported."""
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8 or higher is required for RSMT")

def main():
    """Main setup function."""
    check_python_version()
    
    setup(
        name="rsmt",
        version=get_version(),
        description="Real-time Stylized Motion Transition - Deep learning framework for character animation",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        
        # Author information
        author="RSMT Development Team",
        author_email="rsmt@example.com",
        maintainer="RSMT Development Team",
        maintainer_email="rsmt@example.com",
        
        # URLs
        url="https://github.com/rsmt-project/rsmt",
        project_urls={
            "Documentation": "https://rsmt.readthedocs.io",
            "Source Code": "https://github.com/rsmt-project/rsmt",
            "Bug Tracker": "https://github.com/rsmt-project/rsmt/issues",
            "Changelog": "https://github.com/rsmt-project/rsmt/blob/main/CHANGELOG.md",
        },
        
        # Package discovery
        packages=find_packages(
            where=".",
            include=["rsmt*", "scripts*"],
            exclude=["tests*", "docs*", "tools*"],
        ),
        package_dir={"": "."},
        package_data=PACKAGE_DATA,
        include_package_data=True,
        
        # Dependencies
        python_requires=">=3.8",
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        
        # Entry points
        entry_points=ENTRY_POINTS,
        
        # Metadata
        license="MIT",
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        
        # Options
        zip_safe=False,
        platforms=["any"],
        
        # Additional metadata
        provides=["rsmt"],
    )

if __name__ == "__main__":
    main()
