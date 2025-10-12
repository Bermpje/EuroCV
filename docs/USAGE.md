# EuroCV Usage Guide

Complete guide for using EuroCV in different scenarios.

## Table of Contents

1. [Installation](#installation)
2. [CLI Usage](#cli-usage)
3. [Python API](#python-api)
4. [HTTP API](#http-api)
5. [Docker Usage](#docker-usage)
6. [Advanced Features](#advanced-features)
7. [Configuration](#configuration)

## Installation

### From PyPI

```bash
pip install eurocv
```

### With OCR Support

```bash
pip install eurocv[ocr]

# System dependencies:
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-nld

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### From Source

```bash
git clone https://github.com/yourusername/eurocv.git
cd eurocv
pip install -e ".[dev,ocr]"
```

## CLI Usage

### Basic Conversion

```bash
# Convert to JSON (default)
eurocv convert resume.pdf

# Specify output file
eurocv convert resume.pdf --out output.json

# Convert to both JSON and XML
eurocv convert resume.docx --out-json cv.json --out-xml cv.xml
```

### With Options

```bash
# Dutch locale, no photo (GDPR-friendly)
eurocv convert resume.pdf --locale nl-NL --no-photo --out output.json

# Use OCR for scanned PDFs
eurocv convert scanned.pdf --ocr --out output.json

# Skip validation
eurocv convert resume.pdf --no-validate --out output.json
```

### Batch Processing

```bash
# Process all PDFs in a directory
eurocv batch "resumes/*.pdf" --out-dir output/

# Parallel processing
eurocv batch "*.pdf" --out-dir output/ --parallel 4

# Dutch locale for all files
eurocv batch "*.docx" --out-dir output/ --locale nl-NL --no-photo
```

### Validation

```bash
# Validate a Europass JSON file
eurocv validate europass.json

# Validate a Europass XML file
eurocv validate europass.xml
```

### Start HTTP Server

```bash
# Start API server
eurocv serve

# Custom host and port
eurocv serve --host 0.0.0.0 --port 8080

# With auto-reload (development)
eurocv serve --reload
```

## Python API

### Basic Usage

```python
from eurocv import convert_to_europass

# Simple conversion
europass_json = convert_to_europass("resume.pdf")

# Save to file
import json
with open("output.json", "w") as f:
    json.dump(europass_json, f, indent=2)
```

### With Options

```python
from eurocv import convert_to_europass

# Full options
europass_json = convert_to_europass(
    "resume.pdf",
    locale="nl-NL",           # Dutch formatting
    include_photo=False,      # No photo (GDPR)
    output_format="json",     # json, xml, or both
    use_ocr=False,            # OCR for scanned PDFs
    validate=True             # Validate output
)
```

### Get Both Formats

```python
from eurocv import convert_to_europass

result = convert_to_europass("resume.pdf", output_format="both")

# Access JSON
print(result.json["DocumentInfo"])

# Access XML
print(result.xml)

# Check validation
if result.validation_errors:
    print("Validation errors:", result.validation_errors)
```

### Advanced API

```python
from eurocv.core.converter import extract_resume, map_to_europass, validate_europass

# Step-by-step processing
resume = extract_resume("resume.pdf", use_ocr=False)

# Modify resume data if needed
resume.personal_info.email = "new@email.com"

# Map to Europass
europass = map_to_europass(resume, locale="nl-NL")

# Get output
europass_json = europass.to_json()
europass_xml = europass.to_xml()

# Validate
is_valid, errors = validate_europass(europass_json)
```

## HTTP API

### Starting the Server

```bash
# Using CLI
eurocv serve --host 0.0.0.0 --port 8000

# Using uvicorn
uvicorn eurocv.api.main:app --host 0.0.0.0 --port 8000

# With Docker
docker run -p 8000:8000 ghcr.io/yourusername/eurocv serve
```

### API Endpoints

#### Convert Resume

```bash
curl -X POST http://localhost:8000/convert \
  -F "file=@resume.pdf" \
  -F "locale=nl-NL" \
  -F "include_photo=false" \
  -F "output_format=json"
```

Response:
```json
{
  "success": true,
  "data": {
    "DocumentInfo": { ... },
    "LearnerInfo": { ... }
  },
  "validation_errors": [],
  "message": "Conversion successful"
}
```

#### Validate Europass Data

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d @europass.json
```

Response:
```json
{
  "is_valid": true,
  "errors": []
}
```

#### Health Check

```bash
curl http://localhost:8000/healthz
```

#### Service Info

```bash
curl http://localhost:8000/info
```

### Python Client

```python
import requests

# Convert a file
with open("resume.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/convert",
        files={"file": f},
        data={
            "locale": "nl-NL",
            "include_photo": False,
            "output_format": "json"
        }
    )

result = response.json()
if result["success"]:
    europass_data = result["data"]
```

## Docker Usage

### Pull Image

```bash
docker pull ghcr.io/yourusername/eurocv:latest
```

### Convert Files

```bash
# Mount current directory
docker run --rm -v $PWD:/data ghcr.io/yourusername/eurocv \
  convert /data/resume.pdf --out /data/output.json

# Batch processing
docker run --rm -v $PWD:/data ghcr.io/yourusername/eurocv \
  batch /data/resumes/*.pdf --out-dir /data/output
```

### Run API Server

```bash
# Using docker run
docker run -p 8000:8000 ghcr.io/yourusername/eurocv serve

# Using docker-compose
docker-compose --profile api up
```

### Development

```bash
# Build and run development image
docker-compose --profile dev up

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Advanced Features

### OCR for Scanned PDFs

```python
from eurocv import convert_to_europass

# Enable OCR
result = convert_to_europass(
    "scanned_resume.pdf",
    use_ocr=True  # Requires tesseract-ocr
)
```

### Custom Extraction

```python
from eurocv.core.extract.pdf_extractor import PDFExtractor

# Create extractor with OCR
extractor = PDFExtractor(use_ocr=True)

# Extract resume
resume = extractor.extract("resume.pdf")

# Access extracted data
print(f"Name: {resume.personal_info.first_name}")
print(f"Email: {resume.personal_info.email}")
print(f"Work Experience: {len(resume.work_experience)} entries")
```

### Custom Mapping

```python
from eurocv.core.map.europass_mapper import EuropassMapper

# Create mapper with custom settings
mapper = EuropassMapper(
    locale="nl-NL",
    include_photo=False
)

# Map resume to Europass
europass = mapper.map(resume)
```

## Configuration

### Environment Variables

```bash
# Set default locale
export EUROCV_LOCALE=nl-NL

# Disable photo by default
export EUROCV_INCLUDE_PHOTO=false

# Enable OCR by default
export EUROCV_USE_OCR=true
```

### Locale Support

Supported locales:
- `en-US` - English (United States)
- `nl-NL` - Dutch (Netherlands)

Date and number formatting will be adjusted based on the selected locale.

## Troubleshooting

### Issue: OCR not working

**Solution**: Install tesseract-ocr system package and Python dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-nld
pip install pytesseract pillow

# macOS
brew install tesseract
pip install pytesseract pillow
```

### Issue: PDF extraction fails

**Solution**: Try different extraction backends:
```python
# Try with OCR
convert_to_europass("file.pdf", use_ocr=True)

# Or use DOCX format if possible
convert_to_europass("file.docx")
```

### Issue: Validation errors

**Solution**: Check validation errors for details:
```python
result = convert_to_europass("file.pdf", output_format="both")
if result.validation_errors:
    for error in result.validation_errors:
        print(f"Error: {error}")
```

## Performance Tips

1. **Batch Processing**: Use `batch` command with `--parallel` for multiple files
2. **Skip Validation**: Use `--no-validate` for faster processing when validation isn't needed
3. **Docker**: Use Docker for consistent performance across environments
4. **OCR**: Disable OCR if files aren't scanned (faster processing)

## Security & Privacy (GDPR/AVG)

1. **No Photo**: Use `--no-photo` or `include_photo=False` to exclude photos
2. **Stateless**: EuroCV doesn't store any data by default
3. **Local Processing**: All processing happens locally (no external APIs)
4. **Temporary Files**: Temporary files are automatically cleaned up

## Support

- Documentation: https://github.com/yourusername/eurocv
- Issues: https://github.com/yourusername/eurocv/issues
- API Docs: http://localhost:8000/docs (when server is running)

