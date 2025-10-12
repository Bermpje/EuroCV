"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a sample PDF file path."""
    pdf_path = tmp_path / "sample.pdf"
    # Note: This is just a path, not an actual PDF
    return pdf_path


@pytest.fixture
def sample_docx_path(tmp_path):
    """Create a sample DOCX file path."""
    docx_path = tmp_path / "sample.docx"
    return docx_path


@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    return out_dir

