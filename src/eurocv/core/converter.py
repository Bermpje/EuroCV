"""Main converter module."""

from pathlib import Path
from typing import Any, Literal, Union

from eurocv.core.extract.docx_extractor import DOCXExtractor
from eurocv.core.extract.pdf_extractor import PDFExtractor
from eurocv.core.map.europass_mapper import EuropassMapper
from eurocv.core.models import ConversionResult, EuropassCV, Resume
from eurocv.core.validate.schema_validator import SchemaValidator


def convert_to_europass(
    file_path: str,
    locale: str = "en-US",
    include_photo: bool = True,
    output_format: Literal["json", "xml", "both"] = "json",
    use_ocr: bool = False,
    validate: bool = True,
) -> Union[dict[str, Any], ConversionResult]:
    """Convert a resume file to Europass format.

    This is the main entry point for the library.

    Args:
        file_path: Path to resume file (PDF or DOCX)
        locale: Locale for formatting (e.g., 'nl-NL', 'en-US')
        include_photo: Whether to include photo (GDPR consideration)
        output_format: Output format - 'json', 'xml', or 'both'
        use_ocr: Use OCR for scanned PDFs (requires pytesseract)
        validate: Validate against Europass schema

    Returns:
        Europass JSON dict if output_format='json',
        ConversionResult object if output_format='both'

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is unsupported
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Step 1: Extract resume data
    resume = extract_resume(str(path), use_ocr=use_ocr)

    # Step 2: Map to Europass format
    europass = map_to_europass(resume, locale=locale, include_photo=include_photo)

    # Step 3: Generate output
    result = ConversionResult()

    if output_format in ["json", "both"]:
        result.json_data = europass.to_json()

    if output_format in ["xml", "both"]:
        result.xml_data = europass.to_xml()

    # Step 4: Validate if requested
    if validate:
        validator = SchemaValidator()

        if result.json_data:
            is_valid, errors = validator.validate_json(result.json_data)
            if not is_valid:
                result.validation_errors.extend(errors)

        if result.xml_data:
            is_valid, errors = validator.validate_xml(result.xml_data)
            if not is_valid:
                result.validation_errors.extend(errors)

    # Return appropriate format
    if output_format == "json":
        return result.json_data or {}
    elif output_format == "xml":
        return result.xml_data or ""
    else:
        return result


def extract_resume(file_path: str, use_ocr: bool = False) -> Resume:
    """Extract resume data from a file.

    Args:
        file_path: Path to resume file
        use_ocr: Use OCR for scanned PDFs

    Returns:
        Resume object

    Raises:
        ValueError: If file format is unsupported
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        extractor = PDFExtractor(use_ocr=use_ocr)
        return extractor.extract(str(path))
    elif suffix in [".docx", ".doc"]:
        extractor = DOCXExtractor()
        return extractor.extract(str(path))
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def map_to_europass(
    resume: Resume, locale: str = "en-US", include_photo: bool = True
) -> EuropassCV:
    """Map Resume to Europass format.

    Args:
        resume: Resume object
        locale: Locale for formatting
        include_photo: Whether to include photo

    Returns:
        EuropassCV object
    """
    mapper = EuropassMapper(locale=locale, include_photo=include_photo)
    return mapper.map(resume)


def validate_europass(data: Union[dict[str, Any], str]) -> tuple[bool, list[str]]:
    """Validate Europass data against schema.

    Args:
        data: Europass JSON dict or XML string

    Returns:
        Tuple of (is_valid, list of errors)
    """
    validator = SchemaValidator()

    if isinstance(data, dict):
        return validator.validate_json(data)
    elif isinstance(data, str):
        return validator.validate_xml(data)
    else:
        return False, ["Invalid data type: must be dict (JSON) or str (XML)"]
