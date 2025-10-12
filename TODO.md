# EuroCV Development TODO

## Project Overview
Build a CLI/API tool that converts resumes (PDF/Word) into Europass XML/JSON output.

## Architecture
```
eurocv/
  /core            # pure library
    /extract       # docx/pdf parsing + heuristics/OCR
    /map           # map source → Europass JSON/XML
    /validate      # schema validation
  /cli             # CLI entrypoint
  /api             # FastAPI service
  /schemas         # pinned Europass schemas
```

## Development Tasks

### ✅ Completed
- [ ] None yet

### 🚧 In Progress
- [ ] Initialize project structure with Python packaging setup

### 📋 TODO

#### Phase 1: Core Setup
- [ ] Initialize project structure with Python packaging setup (pyproject.toml, directory structure)
- [ ] Setup dependencies (PyMuPDF, python-docx, pydantic, typer, fastapi)
- [ ] Create basic project scaffolding

#### Phase 2: Core Extraction
- [ ] Implement PDF extraction using PyMuPDF/pdfminer.six
- [ ] Implement DOCX extraction using python-docx
- [ ] Add OCR fallback with Tesseract for scanned PDFs
- [ ] Create Resume intermediate data model

#### Phase 3: Europass Mapping & Validation
- [ ] Download and pin Europass XML/JSON schemas
- [ ] Implement Europass data model with Pydantic
- [ ] Create mapping logic from Resume → Europass
- [ ] Add schema validation
- [ ] Support CEFR language levels
- [ ] Handle date formatting and localization

#### Phase 4: CLI Interface
- [ ] Build CLI with Typer (convert, batch commands)
- [ ] Add output options (JSON/XML)
- [ ] Implement --no-photo flag (AVG/GDPR compliance)
- [ ] Add --locale support for NL formatting
- [ ] Add progress indicators and error reporting

#### Phase 5: HTTP API
- [ ] Create FastAPI application
- [ ] Implement POST /convert endpoint (multipart upload)
- [ ] Implement POST /validate endpoint
- [ ] Add GET /healthz for liveness checks
- [ ] Add proper error handling and responses

#### Phase 6: Docker & Distribution
- [ ] Create multi-stage Dockerfile (python:slim + tesseract-ocr)
- [ ] Add Docker Compose for development
- [ ] Test batch processing in Docker
- [ ] Setup GitHub Container Registry publishing

#### Phase 7: Testing & Documentation
- [ ] Write unit tests for extraction
- [ ] Write unit tests for mapping
- [ ] Write integration tests for CLI
- [ ] Write integration tests for API
- [ ] Create comprehensive README.md
- [ ] Add usage examples
- [ ] Document API endpoints (OpenAPI/Swagger)

#### Phase 8: Publishing & CI/CD
- [ ] Setup PyPI publishing configuration
- [ ] Create GitHub Actions workflow for tests
- [ ] Create GitHub Actions workflow for Docker builds
- [ ] Add version management
- [ ] Create CHANGELOG.md

## Key Requirements
- ✅ Python-based (good PDF support)
- ✅ Stateless processing (no disk retention)
- ✅ AVG/GDPR compliant (NL/EU)
- ✅ Schema validation against official Europass specs
- ✅ Support both CLI and API interfaces
- ✅ Dockerized for portability

## Example Usage

### CLI
```bash
eurocv convert resume.docx --to europass --out out.json
eurocv convert resume.pdf --out-json output.json --out-xml output.xml --no-photo
eurocv batch resumes/*.pdf --out-dir output/ --parallel 4
```

### Docker
```bash
docker run --rm -v $PWD:/data eurocv convert /data/resume.pdf
```

### Python API
```python
from eurocv import convert_to_europass
europass_json = convert_to_europass("resume.pdf")
```

### HTTP Service
```bash
POST /convert → { "file": "resume.pdf" } → Europass JSON
POST /validate → validation report
GET /healthz → health status
```

## References
- Europass schema: https://interoperable.europe.eu/collection/europass
- Europass data model: e-Profile/CV vocabulary
- EU REST converters: existing endpoints for reference

