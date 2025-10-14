.PHONY: help install lint format type-check test check clean

help:
	@echo "EuroCV Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies and pre-commit hooks"
	@echo ""
	@echo "Checks (same as CI):"
	@echo "  make check          Run all checks (lint, format, type, test)"
	@echo "  make lint           Run ruff linter"
	@echo "  make format         Run ruff formatter"
	@echo "  make type-check     Run mypy type checker"
	@echo "  make test           Run pytest tests"
	@echo ""
	@echo "Git:"
	@echo "  make pre-commit     Run pre-commit on all files"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove build artifacts"

install:
	@echo "📦 Installing dependencies..."
	uv pip install -e ".[dev]"
	@echo "🔧 Installing pre-commit hooks..."
	pre-commit install
	@echo "✅ Setup complete!"

lint:
	@echo "🔍 Running ruff linter..."
	ruff check src/

lint-fix:
	@echo "🔧 Running ruff linter with auto-fix..."
	ruff check src/ --fix

format:
	@echo "✨ Running ruff formatter..."
	ruff format src/

format-check:
	@echo "✨ Checking ruff formatting..."
	ruff format --check src/

type-check:
	@echo "🔎 Running mypy type checker..."
	mypy src/

test:
	@echo "🧪 Running pytest..."
	pytest --cov=eurocv --cov-report=term

test-fast:
	@echo "🧪 Running pytest (fast, no coverage)..."
	pytest -x

# Run all checks (same as GitHub Actions)
check: lint format-check type-check test
	@echo ""
	@echo "✅ All checks passed! Same as CI would run."

# Run pre-commit on all files
pre-commit:
	@echo "🔧 Running pre-commit hooks..."
	pre-commit run --all-files

clean:
	@echo "🧹 Cleaning up..."
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean!"
