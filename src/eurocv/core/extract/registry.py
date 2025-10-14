"""Extractor registry for automatic format detection."""

import logging

from eurocv.core.extract.base_extractor import ResumeExtractor
from eurocv.core.extract.docx_extractor import DOCXExtractor
from eurocv.core.extract.generic_pdf_extractor import GenericPDFExtractor
from eurocv.core.extract.linkedin_pdf_extractor import LinkedInPDFExtractor

logger = logging.getLogger(__name__)

# Extractor priority order (most specific first)
EXTRACTORS: list[type[ResumeExtractor]] = [
    LinkedInPDFExtractor,  # Try LinkedIn first (more specific)
    DOCXExtractor,  # DOCX files
    GenericPDFExtractor,  # Fallback for all PDFs
]


def get_extractor(file_path: str, use_ocr: bool = False) -> ResumeExtractor:
    """Auto-detect and return appropriate extractor for file.

    Iterates through registered extractors in priority order and returns
    the first one that can handle the file.

    Args:
        file_path: Path to the resume file
        use_ocr: Whether to use OCR for scanned PDFs (passed to extractors that support it)

    Returns:
        Initialized extractor instance

    Raises:
        ValueError: If no suitable extractor found for the file

    Example:
        >>> extractor = get_extractor("resume.pdf")
        >>> resume = extractor.extract("resume.pdf")
    """
    for extractor_class in EXTRACTORS:
        # All extractors accept **kwargs, so we can safely pass use_ocr
        extractor = extractor_class(use_ocr=use_ocr)

        # Check if this extractor can handle the file
        if extractor.can_handle(file_path):
            logger.info(f"Selected extractor: {extractor.name} for {file_path}")
            return extractor

    # No suitable extractor found
    raise ValueError(
        f"No suitable extractor found for: {file_path}. "
        f"Supported formats: PDF, DOCX"
    )
