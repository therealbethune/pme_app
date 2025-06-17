# Development Guide

## Quick Start

1. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run all checks (mirrors CI):**
   ```bash
   ./scripts/run_all_checks.sh
   ```

## Individual Commands

### Type Checking
```bash
tox -e typecheck
# or directly:
mypy pme_app/services
```

### Testing
```bash
# Run root tests
tox -e test-root

# Run backend tests
tox -e test-backend

# Run all tests
tox -e all
```

### Coverage
```bash
# Generate coverage report
tox -e coverage-report

# View HTML coverage report
open htmlcov/index.html
```

### Code Quality
```bash
# Format code
black .

# Lint and fix
ruff check --fix .
```

## CI/CD Pipeline

The GitHub Actions workflow:
1. 🏗️ **Sets up Python 3.13**
2. 💾 **Caches pip packages** (60% faster builds)
3. 📦 **Installs pinned dependencies**
4. 🔍 **Runs type checking** (mypy)
5. 🧪 **Runs comprehensive tests** (pytest)
6. 📊 **Generates coverage reports**

## Coverage Thresholds

- **Root tests**: 10% (gradually increasing from 5%)
- **Backend tests**: 80% (maintained high standard)
- **Overall project**: Tracking improvement trend

## Local Development Workflow

1. Make changes
2. Run `./scripts/run_all_checks.sh`
3. Fix any issues
4. Commit changes
5. CI validates automatically

The tox configuration ensures local and CI environments stay synchronized. 