# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Core extraction module for PDF and DOCX files
- Europass mapping with schema validation
- CLI interface with Typer
- FastAPI HTTP service
- Docker support with multi-stage builds
- GitHub Actions CI/CD workflows
- Comprehensive test suite
- Documentation and examples

### Features
- PDF extraction using PyMuPDF and pdfminer.six
- DOCX extraction using python-docx
- Optional OCR support with Tesseract
- Europass JSON and XML output formats
- CEFR language level support
- Dutch (nl-NL) locale support
- GDPR-compliant (no photo option, stateless processing)
- Batch processing support
- Schema validation
- Health check endpoints

## [0.1.0] - 2024-01-01

### Added
- Initial release

