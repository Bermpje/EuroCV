# Contributing to EuroCV

Thanks for your interest in contributing to EuroCV! This guide will help you set up your development environment and understand our workflow.

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/Bermpje/EuroCV.git
cd eurocv
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
make install  # Installs dependencies and pre-commit hooks
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

---

## ✅ Development Workflow

### Run Checks Locally (Same as CI)

We have **three ways** to run the same checks that GitHub Actions runs:

#### Option 1: Makefile (Recommended)

```bash
make check          # Run all checks
make lint           # Run ruff
make format         # Run black
make type-check     # Run mypy
make test           # Run pytest
```

#### Option 2: Check Script

```bash
./scripts/check.sh  # Runs all CI checks
```

#### Option 3: Pre-commit (Automatic)

Pre-commit hooks run automatically on `git commit`:

```bash
git commit -m "your message"  # Hooks run automatically
```

To run manually:

```bash
pre-commit run --all-files
```

---

## 🔧 Development Tools

### Linting (Ruff)

```bash
ruff check src/              # Check for issues
ruff check src/ --fix        # Auto-fix issues
```

### Formatting (Black)

```bash
black src/                   # Format code
black --check src/           # Check formatting
```

### Type Checking (MyPy)

```bash
mypy src/                    # Check types
```

### Testing (Pytest)

```bash
pytest                       # Run all tests
pytest -x                    # Stop on first failure
pytest -k "test_name"        # Run specific test
pytest --cov=eurocv          # With coverage
```

---

## 📋 Code Quality Standards

All code must pass these checks (same as CI):

- ✅ **Ruff**: No linting errors (E501 line length ignored for patterns)
- ✅ **Black**: Code formatted correctly
- ✅ **MyPy**: No critical type errors (warnings are OK)
- ✅ **Pytest**: All tests pass
- ✅ **Pre-commit**: All hooks pass

---

## 🌿 Git Workflow

### 1. Feature Development

```bash
git checkout -b feature/your-feature
# Make changes
make check  # Run all checks
git add .
git commit -m "feat: your feature description"
```

### 2. Push and Create PR

```bash
git push origin feature/your-feature
# Create Pull Request on GitHub
```

### 3. PR Review

- CI checks must pass ✅
- Code review required
- All conversations must be resolved
- Squash and merge to main

---

## 📝 Commit Message Format

Follow conventional commits:

```
feat: add new extraction method
fix: resolve PDF parsing issue
docs: update README
test: add tests for mapper
refactor: improve code structure
style: fix formatting
ci: update GitHub Actions
```

---

## 🔍 CI/CD Pipeline

Our CI runs on:
- ✅ Push to `main`, `develop`, `feature/**`
- ✅ Pull requests to `main`, `develop`

Checks:
- **Tests**: Multiple OS (Ubuntu, macOS, Windows) × Python (3.9-3.12)
- **Linting**: Ruff
- **Formatting**: Black
- **Type Checking**: MyPy
- **Docker**: Build and test

---

## 🛠️ Troubleshooting

### Pre-commit hooks failing?

```bash
pre-commit run --all-files  # See what's failing
make lint-fix               # Auto-fix linting
make format                 # Auto-format
```

### Tests failing?

```bash
pytest -v                   # Verbose output
pytest --lf                 # Run last failed
pytest -x                   # Stop on first failure
```

### Clean build artifacts

```bash
make clean
```

---

## 📚 Additional Resources

- **Project Structure**: See `PROJECT_SUMMARY.md`
- **Usage Examples**: See `docs/USAGE.md`
- **API Documentation**: See `docs/API.md`
- **Europass Schema**: See `docs/EUROPASS_SCHEMA_V3.4.md`

---

## 💡 Need Help?

- Open an issue on GitHub
- Check existing issues and PRs
- Review the documentation in `docs/`

---

## 🎉 Thank You!

Your contributions make EuroCV better for everyone! 🚀
