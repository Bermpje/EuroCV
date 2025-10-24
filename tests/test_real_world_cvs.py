"""Real-world CV testing with actual resume files.

These tests are designed to work with real CVs from the input/ folder.
Tests are skipped if the input files are not present, making them safe for CI/CD.
"""

from pathlib import Path

import pytest

from eurocv.core.converter import convert_to_europass


def cv_file_exists(filename: str) -> bool:
    """Check if a CV file exists in the input folder."""
    input_folder = Path(__file__).parent.parent / "input"
    return (input_folder / filename).exists()


@pytest.mark.skipif(
    not cv_file_exists("CV Lotte Kremers_0825NL .pdf"),
    reason="Lotte's CV not available (contains PII, not in repo)",
)
def test_lotte_dutch_pdf():
    """Test extraction from Lotte's Dutch CV (generic PDF format)."""
    input_folder = Path(__file__).parent.parent / "input"
    cv_path = input_folder / "CV Lotte Kremers_0825NL .pdf"

    result = convert_to_europass(str(cv_path), output_format="both")

    # Verify basic extraction worked
    assert result.json_data is not None
    assert result.xml_data is not None

    # Check key fields are extracted (basic smoke test)
    import json

    data = (
        json.loads(result.json_data)
        if isinstance(result.json_data, str)
        else result.json_data
    )
    assert "SkillsPassport" in data or "Europass" in str(data) or "LearnerInfo" in data


@pytest.mark.skipif(
    not cv_file_exists("CV Emiel Kremers - november 2021.docx"),
    reason="Emiel's CV not available (contains PII, not in repo)",
)
def test_emiel_dutch_docx():
    """Test extraction from Emiel's Dutch CV (DOCX format)."""
    input_folder = Path(__file__).parent.parent / "input"
    cv_path = input_folder / "CV Emiel Kremers - november 2021.docx"

    result = convert_to_europass(str(cv_path), output_format="both")

    # Verify basic extraction worked
    assert result.json_data is not None
    assert result.xml_data is not None

    # Check DOCX extraction worked (basic smoke test)
    import json

    data = (
        json.loads(result.json_data)
        if isinstance(result.json_data, str)
        else result.json_data
    )
    assert "SkillsPassport" in data or "Europass" in str(data) or "LearnerInfo" in data


# Additional real-world CV tests can be added here as new CVs are provided
# Pattern:
# @pytest.mark.skipif(not cv_file_exists("filename.pdf"), reason="CV not available")
# def test_new_cv():
#     """Test description"""
#     result = convert_to_europass(str(cv_path), output_format="both")
#     assert result.json is not None
