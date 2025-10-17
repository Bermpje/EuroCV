"""Base extractor interface for resume extraction."""

from abc import ABC, abstractmethod
from typing import Any

from eurocv.core.models import Resume


class ResumeExtractor(ABC):
    """Abstract base class for resume extractors.

    All resume extractors must inherit from this class and implement
    the required methods for extraction and file type detection.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize extractor.

        Subclasses may accept specific parameters (e.g. use_ocr for PDF extractors).
        This base implementation accepts any keyword arguments for flexibility.
        """
        pass

    @abstractmethod
    def extract(self, file_path: str) -> Resume:
        """Extract resume data from file.

        Args:
            file_path: Path to the resume file

        Returns:
            Resume object with extracted data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid or unsupported
        """
        pass

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """Check if this extractor can handle the given file.

        This method is used for auto-detection to determine which
        extractor should be used for a given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this extractor can handle the file, False otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this extractor.

        Used for logging and debugging purposes.

        Returns:
            Human-readable name of the extractor
        """
        pass
