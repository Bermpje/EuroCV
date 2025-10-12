"""Basic usage examples for EuroCV."""

from eurocv import convert_to_europass
import json


def example_basic_conversion():
    """Basic conversion example."""
    print("Example 1: Basic conversion")
    print("-" * 50)
    
    # Convert PDF to Europass JSON
    result = convert_to_europass("resume.pdf")
    
    # Print the result
    print(json.dumps(result, indent=2))
    
    # Save to file
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n✓ Conversion complete! Output saved to output.json\n")


def example_with_options():
    """Conversion with options."""
    print("Example 2: Conversion with options")
    print("-" * 50)
    
    # Convert with Dutch locale and no photo
    result = convert_to_europass(
        "resume.pdf",
        locale="nl-NL",
        include_photo=False,  # GDPR-friendly
        output_format="json",
        use_ocr=False,
        validate=True
    )
    
    print("Conversion successful!")
    print(f"Document type: {result['DocumentInfo']['DocumentType']}")
    print(f"Generated: {result['DocumentInfo']['CreationDate']}")


def example_both_formats():
    """Get both JSON and XML output."""
    print("\nExample 3: Get both JSON and XML")
    print("-" * 50)
    
    result = convert_to_europass(
        "resume.pdf",
        output_format="both"
    )
    
    # Access JSON
    print(f"JSON keys: {list(result.json.keys())}")
    
    # Access XML
    print(f"XML length: {len(result.xml)} characters")
    
    # Check validation errors
    if result.validation_errors:
        print("⚠ Validation warnings:")
        for error in result.validation_errors:
            print(f"  - {error}")
    else:
        print("✓ No validation errors")


def example_batch_processing():
    """Batch process multiple files."""
    print("\nExample 4: Batch processing (using CLI)")
    print("-" * 50)
    
    import subprocess
    
    # Use CLI for batch processing
    cmd = [
        "eurocv",
        "batch",
        "resumes/*.pdf",
        "--out-dir",
        "output/",
        "--parallel",
        "4",
        "--locale",
        "nl-NL"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    # subprocess.run(cmd)


def example_api_usage():
    """Using the Python API programmatically."""
    print("\nExample 5: Advanced API usage")
    print("-" * 50)
    
    from eurocv.core.converter import extract_resume, map_to_europass, validate_europass
    
    # Step 1: Extract resume data
    resume = extract_resume("resume.pdf")
    print(f"✓ Extracted resume for: {resume.personal_info.first_name}")
    
    # Step 2: Map to Europass
    europass = map_to_europass(resume, locale="nl-NL", include_photo=False)
    print("✓ Mapped to Europass format")
    
    # Step 3: Validate
    is_valid, errors = validate_europass(europass.to_json())
    if is_valid:
        print("✓ Validation passed!")
    else:
        print(f"⚠ Validation errors: {len(errors)}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EuroCV - Usage Examples")
    print("=" * 70 + "\n")
    
    # Note: These examples assume you have a resume.pdf file
    # Uncomment to run:
    
    # example_basic_conversion()
    # example_with_options()
    # example_both_formats()
    # example_batch_processing()
    # example_api_usage()
    
    print("\n" + "=" * 70)
    print("To run these examples, uncomment the function calls above")
    print("and ensure you have a sample resume.pdf file in the same directory")
    print("=" * 70 + "\n")

