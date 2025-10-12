.PHONY: help install install-dev test lint format type-check clean build publish docker-build docker-run docs

help:
	@echo "Available commands:"
	@echo "  make install       - Install package"
	@echo "  make install-dev   - Install package with dev dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"
	@echo "  make type-check    - Run type checker"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make build         - Build package"
	@echo "  make publish       - Publish to PyPI"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,ocr]"

test:
	pytest --cov=eurocv --cov-report=html --cov-report=term

test-fast:
	pytest -x --ff

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine check dist/*
	twine upload dist/*

publish-test: build
	twine check dist/*
	twine upload --repository testpypi dist/*

docker-build:
	docker build -t eurocv:latest .

docker-build-dev:
	docker build -f Dockerfile.dev -t eurocv:dev .

docker-run:
	docker run --rm -v $(PWD)/data:/data eurocv:latest --help

docker-compose-up:
	docker-compose --profile api up -d

docker-compose-down:
	docker-compose down

dev-server:
	uvicorn eurocv.api.main:app --reload --host 0.0.0.0 --port 8000

all: format lint type-check test

