# EuroCV

Convert resumes (PDF/DOCX) to Europass XML/JSON format with CLI, Python API, and HTTP service support.

## Features

- 📄 **Multi-format support**: Parse PDF and DOCX resumes with auto-detection
- 🤖 **Smart Extractors**: LinkedIn PDF, Generic PDF (with Dutch support), and DOCX extractors
- 🌍 **Multi-language**: Native support for English and Dutch resumes
- 🇪🇺 **Europass compliant**: Validates against official Europass schemas
- 🐍 **Python API**: Use as a library in your Python projects
- 💻 **CLI tool**: Command-line interface for batch processing
- 🌐 **HTTP service**: FastAPI-based REST API
- 🐳 **Docker ready**: Containerized for easy deployment
- 🔒 **AVG/GDPR compliant**: Stateless processing, no data retention
- 🌍 **Multi-locale**: Support for multiple date/number formats (including Dutch)

## Installation

### From PyPI (coming soon)

```bash
pip install eurocv
```

### From source

```bash
git clone https://github.com/emiel/eurocv.git
cd eurocv
pip install -e .
```

### With OCR support

```bash
pip install eurocv[ocr]
# Also requires tesseract-ocr system package
```

### Docker

```bash
docker pull ghcr.io/emiel/eurocv:latest
```

## Usage

### CLI

```bash
# Convert single file
eurocv convert resume.pdf --out output.json

# Convert with XML output
eurocv convert resume.docx --out-json output.json --out-xml output.xml

# Batch conversion
eurocv batch resumes/*.pdf --out-dir output/ --parallel 4

# Dutch locale and no photo (GDPR-friendly)
eurocv convert cv.pdf --locale nl-NL --no-photo --out output.json
```

### Python API

```python
from eurocv import convert_to_europass

# Simple conversion
europass_json = convert_to_europass("resume.pdf")

# With options
europass_json = convert_to_europass(
    "resume.pdf",
    locale="nl-NL",
    include_photo=False,
    output_format="json"
)

# Get both JSON and XML
result = convert_to_europass("resume.pdf", output_format="both")
print(result.json)
print(result.xml)
```

### Docker

```bash
# Convert a file
docker run --rm -v $PWD:/data ghcr.io/emiel/eurocv \
  convert /data/resume.pdf --out /data/output.json

# Batch processing
docker run --rm -v $PWD:/data ghcr.io/emiel/eurocv \
  batch /data/resumes/*.pdf --out-dir /data/output
```

### HTTP Service

Start the server:

```bash
# Using CLI
eurocv serve --host 0.0.0.0 --port 8000

# Using Docker
docker run -p 8000:8000 ghcr.io/emiel/eurocv serve

# Using uvicorn directly
uvicorn eurocv.api.main:app --host 0.0.0.0 --port 8000
```

API endpoints:

```bash
# Convert a resume
curl -X POST http://localhost:8000/convert \
  -F "file=@resume.pdf" \
  -F "locale=nl-NL" \
  -F "include_photo=false"

# Validate Europass JSON
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d @europass.json

# Health check
curl http://localhost:8000/healthz
```

## Architecture

```
eurocv/
├── core/
│   ├── extract/      # PDF/DOCX parsing
│   ├── map/          # Resume → Europass mapping
│   └── validate/     # Schema validation
├── cli/              # CLI interface (Typer)
├── api/              # HTTP service (FastAPI)
└── schemas/          # Europass XML/JSON schemas
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/emiel/eurocv.git
cd eurocv

# Install with dev dependencies
pip install -e ".[dev,ocr]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

### Running locally

```bash
# CLI
python -m eurocv.cli.main convert test.pdf --out output.json

# API server
uvicorn eurocv.api.main:app --reload
```

### Docker build

```bash
# Build image
docker build -t eurocv:local .

# Run
docker run --rm -v $PWD:/data eurocv:local convert /data/test.pdf
```

## Privacy & Compliance (AVG/GDPR)

- **Stateless processing**: No data is stored on disk
- **No photo by default**: Use `--no-photo` flag to exclude photos (GDPR-friendly)
- **Local processing**: Run in your own infrastructure
- **Encrypted storage**: Use `--store=encrypted` only when necessary

## Europass Resources

- [Europass Schema](https://interoperable.europe.eu/collection/europass)
- [Europass Data Model](https://joinup.ec.europa.eu/collection/europass)
- [CEFR Language Levels](https://www.coe.int/en/web/common-european-framework-reference-languages)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: https://github.com/emiel/eurocv/issues
- Email: [your-email]

## Roadmap

- [ ] Support for JSON Resume format
- [ ] Enhanced OCR with layout analysis
- [ ] Support for more input formats (LinkedIn, etc.)
- [ ] AI-powered field extraction
- [ ] Europass PDF rendering
- [ ] Multi-language support
