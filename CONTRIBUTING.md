# Contributing to EuroCV

Thank you for your interest in contributing to EuroCV! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/eurocv.git
   cd eurocv
   ```

3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev,ocr]"
   ```

4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run these before committing:

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Testing

We use pytest for testing. Write tests for all new features and bug fixes.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=eurocv --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_personal_info_creation
```

### Running Locally

#### CLI
```bash
# Run CLI
python -m eurocv.cli.main convert test.pdf --out output.json
```

#### API Server
```bash
# Run API server with auto-reload
uvicorn eurocv.api.main:app --reload
```

#### Docker
```bash
# Build and run
docker build -t eurocv:dev .
docker run --rm -v $PWD:/data eurocv:dev convert /data/test.pdf
```

## Pull Request Process

1. **Update tests**: Add or update tests for your changes
2. **Update documentation**: Update README.md, docstrings, and comments
3. **Run the test suite**: Ensure all tests pass
4. **Update CHANGELOG.md**: Add your changes under "Unreleased"
5. **Commit your changes**: Use clear, descriptive commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**: Provide a clear description of your changes

### Commit Message Guidelines

Use clear, descriptive commit messages following this format:

```
type(scope): brief description

Longer description if needed

Fixes #issue_number
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(extractor): add support for OCR in PDF extraction
fix(mapper): correct date formatting for nl-NL locale
docs(readme): add Docker usage examples
```

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

Reviewers will check for:
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations (especially for file handling)

## Bug Reports

When filing a bug report, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Minimal example to reproduce the bug
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: OS, Python version, package versions
6. **Sample files**: If relevant (anonymized resumes)

## Feature Requests

We welcome feature requests! Please include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other solutions you've considered
4. **Additional context**: Any other relevant information

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

Examples of unacceptable behavior:
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

