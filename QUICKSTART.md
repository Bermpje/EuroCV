# EuroCV Quick Start Guide

Get up and running with EuroCV in 5 minutes!

## Installation

```bash
pip install eurocv
```

## Quick Examples

### 1. Convert a Resume (CLI)

```bash
eurocv convert resume.pdf --out output.json
```

### 2. Convert with Locale Support (GDPR-friendly)

```bash
eurocv convert resume.pdf --locale nl-NL --no-photo --out output.json
```

### 3. Batch Process Multiple Files

```bash
eurocv batch "resumes/*.pdf" --out-dir output/ --parallel 4
```

### 4. Python API Usage

```python
from eurocv import convert_to_europass

# Convert and get JSON
europass_json = convert_to_europass("resume.pdf")

# With options
europass_json = convert_to_europass(
    "resume.pdf",
    locale="nl-NL",
    include_photo=False
)
```

### 5. Start HTTP API Server

```bash
# Start server
eurocv serve

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### 6. Convert via HTTP API

```bash
curl -X POST http://localhost:8000/convert \
  -F "file=@resume.pdf" \
  -F "locale=nl-NL" \
  -F "include_photo=false"
```

### 7. Docker Usage

```bash
# Pull image
docker pull ghcr.io/yourusername/eurocv:latest

# Convert a file
docker run --rm -v $PWD:/data ghcr.io/yourusername/eurocv \
  convert /data/resume.pdf --out /data/output.json

# Start API server
docker run -p 8000:8000 ghcr.io/yourusername/eurocv serve
```

## Next Steps

- 📖 Read the [full documentation](docs/USAGE.md)
- 💻 Check out [examples](examples/)
- 🐛 Report issues on [GitHub](https://github.com/yourusername/eurocv/issues)
- 🤝 See [contributing guidelines](CONTRIBUTING.md)

## Key Features

✅ PDF and DOCX support  
✅ Europass JSON and XML output  
✅ CLI, Python API, and HTTP service  
✅ Docker support  
✅ OCR for scanned PDFs  
✅ GDPR/AVG compliant  
✅ Dutch locale support  
✅ Batch processing  
✅ Schema validation  

## Common Use Cases

### Use Case 1: Individual Conversion
```bash
eurocv convert my-resume.pdf --out europass.json
```

### Use Case 2: Batch Processing for Recruitment
```bash
eurocv batch "applications/*.pdf" \
  --out-dir processed/ \
  --locale nl-NL \
  --no-photo \
  --parallel 8
```

### Use Case 3: Integration with Existing System
```python
from eurocv import convert_to_europass

def process_application(file_path):
    try:
        europass = convert_to_europass(
            file_path,
            locale="nl-NL",
            include_photo=False,
            validate=True
        )
        # Store in database, send to API, etc.
        return europass
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None
```

### Use Case 4: Microservice Deployment
```yaml
# docker-compose.yml
services:
  eurocv:
    image: ghcr.io/yourusername/eurocv:latest
    command: serve --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    restart: unless-stopped
```

## Troubleshooting

### Issue: Command not found
**Solution**: Make sure eurocv is installed: `pip install eurocv`

### Issue: PDF extraction fails
**Solution**: Try with OCR: `eurocv convert file.pdf --ocr --out output.json`

### Issue: Need better accuracy
**Solution**: Use DOCX format instead of PDF when possible

## Support

- 📧 Email: your-email@example.com
- 💬 GitHub Issues: https://github.com/yourusername/eurocv/issues
- 📚 Full Docs: [USAGE.md](docs/USAGE.md)

---

**License**: MIT  
**Author**: Emiel Kremers  
**Repository**: https://github.com/yourusername/eurocv

