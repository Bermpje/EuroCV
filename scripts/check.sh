#!/bin/bash
# Run the same checks as GitHub Actions CI
# Usage: ./scripts/check.sh

set -e

echo "🔍 Running CI checks locally..."
echo "==============================="
echo ""

echo "📋 1/4 Linting with ruff..."
ruff check src/
echo "✅ Lint passed!"
echo ""

echo "📋 2/4 Format check with black..."
black --check src/
echo "✅ Format check passed!"
echo ""

echo "📋 3/4 Type check with mypy..."
mypy src/
echo "✅ Type check passed!"
echo ""

echo "📋 4/4 Tests with pytest..."
pytest --cov=eurocv --cov-report=term
echo "✅ Tests passed!"
echo ""

echo "🎉 All CI checks passed!"
echo "========================"
echo ""
echo "Your code is ready to push! 🚀"

