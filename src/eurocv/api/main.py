"""FastAPI HTTP service for EuroCV."""

import tempfile
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from eurocv import __version__
from eurocv.core.converter import convert_to_europass, validate_europass

# Create FastAPI app
app = FastAPI(
    title="EuroCV API",
    description="Convert resumes (PDF/DOCX) to Europass XML/JSON format",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


class ConvertRequest(BaseModel):
    """Convert request parameters."""
    locale: str = "en-US"
    include_photo: bool = True
    output_format: str = "json"  # json, xml, or both
    use_ocr: bool = False
    validate: bool = True


class ConvertResponse(BaseModel):
    """Convert response."""
    success: bool
    data: Optional[dict[str, Any]] = None
    xml: Optional[str] = None
    validation_errors: list[str] = []
    message: Optional[str] = None


class ValidateRequest(BaseModel):
    """Validation request."""
    data: dict[str, Any]


class ValidateResponse(BaseModel):
    """Validation response."""
    is_valid: bool
    errors: list[str] = []


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "EuroCV API",
        "version": __version__,
        "docs": "/docs",
        "health": "/healthz",
    }


@app.get("/healthz")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": __version__}


@app.post("/convert", response_model=ConvertResponse)
async def convert(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    locale: str = Form("en-US", description="Locale for formatting (e.g., nl-NL)"),
    include_photo: bool = Form(True, description="Include photo in output"),
    output_format: str = Form("json", description="Output format: json, xml, or both"),
    use_ocr: bool = Form(False, description="Use OCR for scanned PDFs"),
    validate: bool = Form(True, description="Validate against Europass schema"),
) -> ConvertResponse:
    """Convert a resume file to Europass format.

    Upload a PDF or DOCX resume file and get back Europass JSON/XML.

    Parameters:
    - **file**: Resume file (PDF or DOCX)
    - **locale**: Locale for date/number formatting (default: en-US)
    - **include_photo**: Whether to include photo (default: true)
    - **output_format**: Output format - json, xml, or both (default: json)
    - **use_ocr**: Use OCR for scanned PDFs (default: false)
    - **validate**: Validate output against schema (default: true)

    Returns:
    - **success**: Whether conversion succeeded
    - **data**: Europass JSON data (if output_format is json or both)
    - **xml**: Europass XML string (if output_format is xml or both)
    - **validation_errors**: List of validation errors/warnings
    - **message**: Status message
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: .pdf, .docx, .doc"
        )

    # Validate output format
    if output_format not in ['json', 'xml', 'both']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_format: {output_format}. Must be: json, xml, or both"
        )

    # Save uploaded file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Convert
        result = convert_to_europass(
            tmp_path,
            locale=locale,
            include_photo=include_photo,
            output_format=output_format,
            use_ocr=use_ocr,
            validate=validate,
        )

        # Clean up temp file
        Path(tmp_path).unlink()

        # Build response
        if output_format == "json":
            return ConvertResponse(
                success=True,
                data=result,
                message="Conversion successful"
            )
        elif output_format == "xml":
            return ConvertResponse(
                success=True,
                xml=result,
                message="Conversion successful"
            )
        else:  # both
            return ConvertResponse(
                success=True,
                data=result.json,
                xml=result.xml,
                validation_errors=result.validation_errors,
                message="Conversion successful"
            )

    except Exception as e:
        # Clean up temp file on error
        if 'tmp_path' in locals():
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.post("/validate", response_model=ValidateResponse)
async def validate_endpoint(request: ValidateRequest) -> ValidateResponse:
    """Validate Europass JSON data against the schema.

    Parameters:
    - **data**: Europass JSON data to validate

    Returns:
    - **is_valid**: Whether the data is valid
    - **errors**: List of validation errors
    """
    try:
        is_valid, errors = validate_europass(request.data)

        return ValidateResponse(
            is_valid=is_valid,
            errors=errors
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/info")
async def info() -> dict[str, Any]:
    """Get service information and capabilities."""
    return {
        "service": "EuroCV API",
        "version": __version__,
        "capabilities": {
            "input_formats": ["pdf", "docx", "doc"],
            "output_formats": ["json", "xml"],
            "locales": ["en-US", "nl-NL"],
            "ocr": True,
            "validation": True,
        },
        "endpoints": {
            "convert": "/convert",
            "validate": "/validate",
            "health": "/healthz",
            "docs": "/docs",
        }
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found. See /docs for available endpoints."}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."}
    )

