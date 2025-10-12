#!/bin/bash
# Release script for EuroCV

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}EuroCV Release Script${NC}"
echo "====================="
echo ""

# Check if on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo -e "${RED}Error: Must be on main branch to release${NC}"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}Error: There are uncommitted changes${NC}"
    git status --short
    exit 1
fi

# Get current version
current_version=$(grep "version = " pyproject.toml | cut -d'"' -f2)
echo -e "Current version: ${YELLOW}$current_version${NC}"

# Ask for new version
read -p "Enter new version (e.g., 0.2.0): " new_version

if [ -z "$new_version" ]; then
    echo -e "${RED}Error: Version cannot be empty${NC}"
    exit 1
fi

echo ""
echo -e "Preparing release ${YELLOW}v$new_version${NC}..."
echo ""

# Update version in pyproject.toml
sed -i.bak "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
rm pyproject.toml.bak

# Update version in __init__.py
sed -i.bak "s/__version__ = \"$current_version\"/__version__ = \"$new_version\"/" src/eurocv/__init__.py
rm src/eurocv/__init__.py.bak

# Update CHANGELOG.md
today=$(date +%Y-%m-%d)
sed -i.bak "s/## \[Unreleased\]/## [Unreleased]\n\n## [$new_version] - $today/" CHANGELOG.md
rm CHANGELOG.md.bak

echo "✓ Updated version numbers"

# Run tests
echo ""
echo "Running tests..."
make test

echo "✓ Tests passed"

# Build package
echo ""
echo "Building package..."
make build

echo "✓ Package built"

# Commit changes
echo ""
echo "Committing changes..."
git add pyproject.toml src/eurocv/__init__.py CHANGELOG.md
git commit -m "chore: bump version to $new_version"

# Create tag
echo "Creating tag v$new_version..."
git tag -a "v$new_version" -m "Release version $new_version"

echo ""
echo -e "${GREEN}✓ Release v$new_version prepared!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git show"
echo "  2. Push to remote: git push origin main --tags"
echo "  3. Create a GitHub release from the tag"
echo "  4. GitHub Actions will automatically publish to PyPI"
echo ""
echo "To undo this release:"
echo "  git tag -d v$new_version"
echo "  git reset --hard HEAD~1"

