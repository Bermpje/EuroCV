"""Example API client for EuroCV HTTP service."""

import requests
from pathlib import Path


class EuroCVClient:
    """Client for EuroCV API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip("/")
    
    def health_check(self) -> dict:
        """Check API health.
        
        Returns:
            Health status dict
        """
        response = requests.get(f"{self.base_url}/healthz")
        response.raise_for_status()
        return response.json()
    
    def convert(
        self,
        file_path: str,
        locale: str = "en-US",
        include_photo: bool = True,
        output_format: str = "json",
        use_ocr: bool = False,
    ) -> dict:
        """Convert a resume file.
        
        Args:
            file_path: Path to resume file
            locale: Locale for formatting
            include_photo: Include photo in output
            output_format: Output format (json/xml/both)
            use_ocr: Use OCR for scanned PDFs
            
        Returns:
            Conversion result
        """
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            data = {
                "locale": locale,
                "include_photo": include_photo,
                "output_format": output_format,
                "use_ocr": use_ocr,
            }
            
            response = requests.post(
                f"{self.base_url}/convert",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    def validate(self, europass_data: dict) -> dict:
        """Validate Europass data.
        
        Args:
            europass_data: Europass JSON data
            
        Returns:
            Validation result
        """
        response = requests.post(
            f"{self.base_url}/validate",
            json={"data": europass_data}
        )
        response.raise_for_status()
        return response.json()
    
    def info(self) -> dict:
        """Get service information.
        
        Returns:
            Service info
        """
        response = requests.get(f"{self.base_url}/info")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage."""
    # Initialize client
    client = EuroCVClient("http://localhost:8000")
    
    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"✓ API is {health['status']}")
    
    # Get service info
    print("\nGetting service info...")
    info = client.info()
    print(f"✓ Service: {info['service']} v{info['version']}")
    print(f"  Capabilities: {', '.join(info['capabilities']['input_formats'])}")
    
    # Convert a file
    print("\nConverting resume...")
    result = client.convert(
        "resume.pdf",
        locale="nl-NL",
        include_photo=False,
        output_format="json"
    )
    
    if result["success"]:
        print("✓ Conversion successful!")
        print(f"  Document type: {result['data']['DocumentInfo']['DocumentType']}")
    else:
        print(f"✗ Conversion failed: {result['message']}")
    
    # Validate the result
    if result["success"]:
        print("\nValidating output...")
        validation = client.validate(result["data"])
        
        if validation["is_valid"]:
            print("✓ Validation passed!")
        else:
            print(f"⚠ Validation errors: {len(validation['errors'])}")
            for error in validation["errors"]:
                print(f"  - {error}")


if __name__ == "__main__":
    main()

