# RSMT CI/CD Quick Start

This guide helps you get started with the CI/CD pipeline in the RSMT project.

## 🚀 Quick Setup (5 minutes)

### 1. Development Environment Setup

```bash
# Clone and enter the repository
cd /home/barberb/RSMT-Realtime-Stylized-Motion-Transition

# Setup development environment automatically
python scripts/setup_dev.py

# Or manual setup:
pip install -e ".[dev,test,docs,gpu]"
pre-commit install
```

### 2. Verify Installation

```bash
# Run quick tests
python tools/testing/run_tests.py --quick

# Check code quality
pre-commit run --all-files

# Build documentation
cd docs && make html
```

## ⚡ Common Commands

### Development Workflow

```bash
# Before making changes
git checkout -b feature/my-feature
python tools/testing/run_tests.py --quick

# During development
black rsmt/ tests/           # Format code
isort rsmt/ tests/          # Sort imports
mypy rsmt/                  # Type check
pytest tests/unit/          # Run tests

# Before committing (automatic with pre-commit)
pre-commit run --all-files
```

### Testing Commands

```bash
# Quick tests (unit tests only)
python tools/testing/run_tests.py --quick

# Full test suite
python tools/testing/run_tests.py --verbose

# Specific test categories
python tools/testing/run_tests.py --unit-only
python tools/testing/run_tests.py --integration-only
python tools/testing/run_tests.py --benchmark-only

# With coverage report
python tools/testing/run_tests.py --coverage
```

### Quality Checks

```bash
# All quality checks
python tools/testing/run_tests.py --quality-only

# Individual checks
black --check rsmt/                    # Code formatting
isort --check-only rsmt/              # Import sorting
flake8 rsmt/                          # Linting
mypy rsmt/                            # Type checking
bandit -r rsmt/                       # Security scan
safety check                          # Dependency security
```

### Documentation

```bash
# Build docs
cd docs
make html                    # HTML documentation
make linkcheck              # Check links
make clean                  # Clean build

# View docs
python -m http.server 8000 -d docs/_build/html
# Open http://localhost:8000
```

### Docker

```bash
# Development container
docker build --target development -t rsmt:dev .
docker run -it -v $(pwd):/app rsmt:dev bash

# Production container
docker build --target production -t rsmt:prod .
docker run -p 8000:8000 rsmt:prod

# GPU container (if CUDA available)
docker build --target gpu -t rsmt:gpu .
docker run --gpus all rsmt:gpu
```

## 🔧 Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| `pyproject.toml` | Project config | Dependencies, tool settings |
| `.pre-commit-config.yaml` | Pre-commit hooks | Quality checks |
| `.github/workflows/ci-cd.yml` | Main CI/CD | Testing, building, deployment |
| `.github/workflows/release.yml` | Release automation | Publishing, tagging |
| `Dockerfile` | Container builds | Multi-stage builds |

## 📋 Checklist for Contributors

### Before First Contribution
- [ ] Run `python scripts/setup_dev.py`
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Verify setup: `python tools/testing/run_tests.py --quick`
- [ ] Read `CODEBASE_REORGANIZATION_PLAN.md`

### For Each Feature/Fix
- [ ] Create feature branch: `git checkout -b feature/name`
- [ ] Write tests for new functionality
- [ ] Run local tests: `python tools/testing/run_tests.py`
- [ ] Check code quality: `pre-commit run --all-files`
- [ ] Update documentation if needed
- [ ] Submit pull request with clear description

### Before Releasing
- [ ] Update version in `pyproject.toml` and `rsmt/__init__.py`
- [ ] Update `CHANGELOG.md`
- [ ] Run full test suite: `python tools/testing/run_tests.py --verbose`
- [ ] Build documentation: `cd docs && make html`
- [ ] Create release tag: `git tag v1.0.0`

## 🎯 Performance Targets

### Test Performance
- **Unit tests**: < 2 minutes
- **Integration tests**: < 5 minutes
- **Full test suite**: < 10 minutes
- **Quality checks**: < 1 minute

### Code Quality
- **Coverage**: ≥ 80%
- **Type coverage**: ≥ 90%
- **Security**: No high/critical issues
- **Performance**: No regressions > 10%

## 🚨 Troubleshooting

### Tests Failing?
```bash
# Get detailed output
python tools/testing/run_tests.py --verbose --tb=long

# Run specific test
pytest tests/unit/test_specific.py::test_function -v

# Debug with pdb
pytest tests/unit/test_specific.py --pdb
```

### Pre-commit Issues?
```bash
# Update hooks
pre-commit autoupdate

# Run specific hook
pre-commit run black --all-files

# Temporarily skip (not recommended)
git commit --no-verify
```

### Docker Problems?
```bash
# Clean rebuild
docker build --no-cache -t rsmt:dev .

# Check logs
docker logs container_name

# Interactive debugging
docker run -it --entrypoint=/bin/bash rsmt:dev
```

### CI/CD Pipeline Issues?
1. Check GitHub Actions tab for detailed logs
2. Verify environment variables are set
3. Check if secrets are configured correctly
4. Ensure branch protection rules allow the action

## 📚 Next Steps

1. **Read the Full Guide**: See `CI_CD_INTEGRATION_GUIDE.md` for comprehensive details
2. **Explore the Codebase**: Check `CODEBASE_REORGANIZATION_PLAN.md` for structure
3. **Contribute**: Look at open issues and submit pull requests
4. **Optimize**: Profile your code and improve performance
5. **Document**: Add documentation for new features

## 💡 Tips

- Use `python tools/testing/run_tests.py --quick` during development
- Set up your IDE to run pre-commit checks on save
- Keep commits small and focused
- Write tests before implementing features (TDD)
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, etc.
- Check the Actions tab on GitHub for CI/CD status

---

Happy coding! 🎉
