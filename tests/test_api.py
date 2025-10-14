"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from eurocv.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_pdf_file(tmp_path):
    """Create a minimal PDF file for testing."""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000229 00000 n
0000000330 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
423
%%EOF"""

    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(pdf_content)
    return pdf_file


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "docs" in data


def test_healthz_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_info_endpoint(client):
    """Test info endpoint."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()

    assert data["service"] == "EuroCV API"
    assert "version" in data
    assert "capabilities" in data
    assert "endpoints" in data

    # Check capabilities
    caps = data["capabilities"]
    assert "pdf" in caps["input_formats"]
    assert "docx" in caps["input_formats"]
    assert "json" in caps["output_formats"]
    assert "xml" in caps["output_formats"]


def test_convert_endpoint_no_file(client):
    """Test convert endpoint without file."""
    response = client.post("/convert")
    assert response.status_code == 422  # Validation error


def test_convert_endpoint_invalid_file_type(client):
    """Test convert endpoint with invalid file type."""
    response = client.post(
        "/convert",
        files={"file": ("test.txt", b"Hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_convert_endpoint_json_format(client, sample_pdf_file):
    """Test convert endpoint with JSON format."""
    with open(sample_pdf_file, "rb") as f:
        response = client.post(
            "/convert",
            files={"file": ("resume.pdf", f, "application/pdf")},
            data={
                "locale": "en-US",
                "output_format": "json",
                "validate": "false",
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"] is not None
    assert data["xml"] is None
    assert "message" in data


def test_convert_endpoint_xml_format(client, sample_pdf_file):
    """Test convert endpoint with XML format."""
    with open(sample_pdf_file, "rb") as f:
        response = client.post(
            "/convert",
            files={"file": ("resume.pdf", f, "application/pdf")},
            data={
                "locale": "en-US",
                "output_format": "xml",
                "validate": "false",
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["xml"] is not None
    assert data["data"] is None


def test_convert_endpoint_both_formats(client, sample_pdf_file):
    """Test convert endpoint with both formats."""
    with open(sample_pdf_file, "rb") as f:
        response = client.post(
            "/convert",
            files={"file": ("resume.pdf", f, "application/pdf")},
            data={
                "locale": "en-US",
                "output_format": "both",
                "validate": "false",
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"] is not None
    assert data["xml"] is not None
    assert isinstance(data["validation_errors"], list)


def test_convert_endpoint_invalid_format(client, sample_pdf_file):
    """Test convert endpoint with invalid format."""
    with open(sample_pdf_file, "rb") as f:
        response = client.post(
            "/convert",
            files={"file": ("resume.pdf", f, "application/pdf")},
            data={
                "output_format": "invalid",
            },
        )

    assert response.status_code == 400
    assert "Invalid output_format" in response.json()["detail"]


def test_convert_endpoint_with_options(client, sample_pdf_file):
    """Test convert endpoint with various options."""
    with open(sample_pdf_file, "rb") as f:
        response = client.post(
            "/convert",
            files={"file": ("resume.pdf", f, "application/pdf")},
            data={
                "locale": "nl-NL",
                "include_photo": "false",
                "use_ocr": "false",
                "validate": "false",
            },
        )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_validate_endpoint_valid_json(client):
    """Test validate endpoint with valid JSON."""
    valid_data = {
        "DocumentInfo": {
            "DocumentType": "EuropassCV",
            "CreationDate": "2024-01-01",
            "LastUpdateDate": "2024-01-01",
            "XSDVersion": "V3.4",
            "Generator": "EuroCV",
        },
        "LearnerInfo": {
            "Identification": {
                "PersonName": {
                    "FirstName": "John",
                    "Surname": "Doe",
                }
            }
        },
    }

    response = client.post("/validate", json={"data": valid_data})
    assert response.status_code == 200
    data = response.json()

    assert "is_valid" in data
    assert isinstance(data["errors"], list)


def test_validate_endpoint_invalid_json(client):
    """Test validate endpoint with invalid JSON."""
    invalid_data = {
        "invalid": "data",
    }

    response = client.post("/validate", json={"data": invalid_data})
    assert response.status_code == 200
    data = response.json()

    assert data["is_valid"] is False
    assert len(data["errors"]) > 0


def test_404_handler(client):
    """Test 404 error handler."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
