#!/bin/bash
# Development environment setup script

set -e

echo "Setting up EuroCV development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.9 or higher is required (found $python_version)"
    exit 1
fi

echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "✓ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-dev.txt

# Install package in editable mode
echo "Installing eurocv in editable mode..."
pip install -e .

# Install OCR dependencies (optional)
echo ""
read -p "Install OCR dependencies (tesseract)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing tesseract on Linux..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-nld
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing tesseract on macOS..."
        brew install tesseract
    else
        echo "Please install tesseract-ocr manually for your OS"
    fi
    
    pip install pytesseract pillow
    echo "✓ OCR dependencies installed"
fi

# Create data directory
mkdir -p data

# Run tests to verify installation
echo ""
echo "Running tests to verify installation..."
pytest tests/ -v

echo ""
echo "✓ Setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start developing:"
echo "  make test          # Run tests"
echo "  make format        # Format code"
echo "  make lint          # Run linter"
echo "  make dev-server    # Start API server"

